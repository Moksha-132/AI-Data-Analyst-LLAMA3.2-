import pandas as pd

def generate_profile_summary(df: pd.DataFrame) -> dict:
    """Generate a basic profiling summary for a DataFrame.
    Returns a dictionary containing:
    - rows, columns count
    - missing values per column
    - data types per column
    - basic statistics for numeric columns (mean, std, min, max)
    """
    profile = {}
    profile["rows"] = df.shape[0]
    profile["columns"] = df.shape[1]
    # Missing values
    missing = df.isnull().sum().to_dict()
    profile["missing_values"] = missing
    # Data types
    dtypes = df.dtypes.apply(lambda x: x.name).to_dict()
    profile["dtypes"] = dtypes
    # Summary stats for numeric columns
    numeric = df.select_dtypes(include='number')
    stats = numeric.describe().to_dict()
    profile["numeric_stats"] = stats
    return profile
