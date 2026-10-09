import numpy as np
import pandas as pd
import pytest
from src.data.download import sha256
from src.evaluation.ml_evaluation import metrics_from_saved,paired_comparison


def test_metrics_are_computed_from_saved_predictions_and_detect_tampering(tmp_path):
    date=pd.Timestamp('2020-01-02')
    data=pd.DataFrame({'date':date,'ticker':list('ABCDE'),'target':[.01,.02,.03,.04,.05],
                       'prediction':[.01,.02,.03,.04,.04],'sample_role':'test','target_available':True})
    path=tmp_path/'pred.parquet';data.to_parquet(path,index=False)
    entry={'path':str(path),'sha256':sha256(path)}
    _,daily,_,metrics=metrics_from_saved(entry,pd.DatetimeIndex([date]),minimum=5)
    assert metrics['MSE']==pytest.approx(.0001/5)
    assert metrics['MAE']==pytest.approx(.01/5)
    assert daily.iloc[0].IC==pytest.approx(np.corrcoef(data.target,data.prediction)[0,1])
    data['prediction']=0.;data.to_parquet(path,index=False)
    with pytest.raises(ValueError,match='checksum'): metrics_from_saved(entry,pd.DatetimeIndex([date]),minimum=5)


def test_paired_delta_keeps_calendar_holes_and_matches_hand_values():
    dates=pd.bdate_range('2020-01-01',periods=4)
    ml=pd.DataFrame({'date':dates,'RankIC':[.2,np.nan,.3,.1]})
    base=pd.DataFrame({'date':dates,'RankIC':[.1,.2,.1,.2]})
    daily,summary=paired_comparison(ml,base,'ML','Ridge')
    np.testing.assert_allclose(daily.delta_RankIC,[.1,np.nan,.2,-.1],equal_nan=True)
    assert summary['mean']==pytest.approx(.2/3)
    assert summary['positive_ratio']==pytest.approx(2/3)
    assert summary['n_dates']==3 and len(daily)==4
