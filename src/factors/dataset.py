"""Frozen Phase 3 matrix assembly and checksum-verified read interface."""
import json
from pathlib import Path

import pandas as pd
import pyarrow.parquet as pq

from src.data.download import sha256
from .definitions import BIAS, NAMES
from .engine import compute_factors
from .preprocessing import preprocess_cross_section
from .targets import HORIZONS, compute_targets


def build_research_matrix(panel, sessions, schedule):
    raw = compute_factors(panel, sessions)
    raw['eligible_at_t'] = panel.is_research_eligible.to_numpy()
    # No target exists at the point preprocessing is executed.
    processed = preprocess_cross_section(raw)
    matrix = raw.merge(processed, on=['date', 'ticker'], validate='one_to_one', sort=False)
    labels = compute_targets(panel, sessions, schedule)
    matrix = matrix.merge(labels, on=['date', 'ticker'], validate='one_to_one', sort=False)
    matrix['is_research_eligible'] = matrix.eligible_at_t
    matrix['eligibility_reason'] = panel.eligibility_reason.to_numpy()
    matrix['last_factor_input_session'] = matrix.date.where(matrix[NAMES].notna().any(axis=1))
    for h in HORIZONS:
        matrix[f'sample_usable_for_research_{h}D'] = matrix.eligible_at_t & matrix.factor_available & matrix[f'target_available_{h}D']
    matrix['sample_usable_for_research'] = matrix.sample_usable_for_research_5D
    for key, value in BIAS.items():
        matrix[key] = value
    return matrix


def load_factor_panel(pointer='data/processed/phase3/research_matrix.json'):
    metadata = json.loads(Path(pointer).read_text(encoding='utf-8'))
    if metadata['status'] != 'PASS' or sha256(metadata['panel_path']) != metadata['panel_sha256']:
        raise ValueError('Phase 3 status/checksum validation failed')
    table = pq.read_table(metadata['panel_path'])
    embedded = json.loads(table.schema.metadata[b'research_metadata'])
    for key in ('survivorship_biased', 'candidate_selection_biased'):
        if metadata.get(key) is not True or embedded.get(key) is not True:
            raise ValueError('Required bias metadata missing')
    return table.to_pandas(), metadata
