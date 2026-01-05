import pandas as pd
import numpy as np

def detect_anomalies(df: pd.DataFrame) -> dict:
    """Detect simple outliers in numeric columns using Z-score.
    Returns a dict mapping column name to a list of row indices considered anomalous.
    """
    anomalies = {}
    numeric_cols = df.select_dtypes(include='number').columns
    for col in numeric_cols:
        series = df[col]
        if series.std() == 0:
            continue
        z_scores = (series - series.mean()) / series.std()
        outlier_idx = np.where(np.abs(z_scores) > 3)[0].tolist()
        if outlier_idx:
            anomalies[col] = outlier_idx
    return anomalies
