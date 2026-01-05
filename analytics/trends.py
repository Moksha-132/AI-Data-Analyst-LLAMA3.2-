import pandas as pd
import numpy as np
from scipy.stats import linregress

def detect_trends(df: pd.DataFrame) -> dict:
    """Detect simple linear trends for numeric columns.
    Returns a dict mapping column name to a description of the trend
    based on the slope of a linear regression.
    """
    trends = {}
    numeric_cols = df.select_dtypes(include='number').columns
    for col in numeric_cols:
        series = df[col].dropna()
        if len(series) < 2:
            continue
        # Use index as x values
        x = np.arange(len(series))
        slope, intercept, r_value, p_value, std_err = linregress(x, series)
        if abs(slope) < 1e-6:
            trend_desc = "no significant trend"
        elif slope > 0:
            trend_desc = f"increasing trend (slope={slope:.4f})"
        else:
            trend_desc = f"decreasing trend (slope={slope:.4f})"
        trends[col] = {
            "description": trend_desc,
            "r_squared": r_value ** 2,
            "p_value": p_value,
        }
    return trends
