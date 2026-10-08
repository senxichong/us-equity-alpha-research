"""Date-local feature transforms with no train/test fit and no target inputs."""
import numpy as np
import pandas as pd

from .definitions import NAMES, PREPROCESSING


def preprocess_cross_section(features):
    """Only explicit raw-factor columns and eligible_at_t determine membership.

    Return winsorized values and population z-scores. Ineligible/missing values,
    sections of fewer than two stocks and zero-variance z-scores stay null.
    """
    if not pd.api.types.is_bool_dtype(features.eligible_at_t):
        raise ValueError('Boolean signal-date eligibility required')
    result = features[['date', 'ticker']].copy()
    values = {}
    for name in NAMES:
        x = features[name].where(features.eligible_at_t & np.isfinite(features[name]))
        group = x.groupby(features.date)
        bounds = group.quantile(PREPROCESSING['winsor_quantiles'], interpolation='linear').unstack()
        lower = features.date.map(bounds[0.01])
        upper = features.date.map(bounds[0.99])
        clipped = x.clip(lower=lower, upper=upper).where(group.transform('count') >= 2)
        clipped_group = clipped.groupby(features.date)
        mean = clipped_group.transform('mean')
        std = clipped_group.transform('std', ddof=0)
        z = (clipped - mean) / std.where(std > 0)
        values[f'{name}_winsorized'] = clipped
        values[f'{name}_zscore'] = z.where(np.isfinite(z))
    result = pd.concat([result, pd.DataFrame(values, index=features.index)], axis=1)
    result['processed_factor_available'] = result[[f'{n}_zscore' for n in NAMES]].notna().all(axis=1)
    return result
