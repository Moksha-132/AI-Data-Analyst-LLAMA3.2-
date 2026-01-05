import pandas as pd

def compute_correlations(df: pd.DataFrame) -> dict:
    """Compute Pearson correlation matrix for numeric columns.
    Returns a dictionary where keys are column pairs "col1-col2" and values are correlation coefficients.
    """
    corr_matrix = df.select_dtypes(include='number').corr()
    correlations = {}
    for i, col1 in enumerate(corr_matrix.columns):
        for col2 in corr_matrix.columns[i+1:]:
            corr_value = corr_matrix.at[col1, col2]
            correlations[f"{col1}-{col2}"] = round(float(corr_value), 4)
    return correlations
