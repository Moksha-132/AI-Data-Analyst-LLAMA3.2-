import pandas as pd
import io
from .profiling import generate_profile_summary
from .trends import detect_trends
from .correlation import compute_correlations
from .anomalies import detect_anomalies

def run_analytics_pipeline(uploaded_file) -> pd.DataFrame:
    """Process the uploaded CSV (path, bytes, or file‑like) and enrich it with analytics.
    Returns the DataFrame with an added attribute `profile_summary` containing a dictionary of profiling, trends, correlations and anomalies.
    """
    # Accept a file path string, raw bytes, or a file‑like object (Flask's FileStorage)
    if isinstance(uploaded_file, str):
        df = pd.read_csv(uploaded_file)
    elif isinstance(uploaded_file, bytes):
        df = pd.read_csv(io.BytesIO(uploaded_file))
    else:
        # Assume file‑like object with a .read() method
        df = pd.read_csv(uploaded_file)

    # Clean noise columns (e.g., Unnamed: 0, index) which are likely CSV indexes
    noise_cols = [c for c in df.columns if 'Unnamed' in c or c.lower() == 'index']
    if noise_cols:
        df = df.drop(columns=noise_cols)

    # Create a sample for expensive AI/Stats operations if dataset is huge
    SAMPLE_SIZE = 2000
    if len(df) > SAMPLE_SIZE:
        sample_df = df.sample(n=SAMPLE_SIZE, random_state=42)
    else:
        sample_df = df

    # Basic profiling (Run on sample to speed up)
    profile = generate_profile_summary(sample_df)
    
    # Overwrite true row/col counts so KPIs remain accurate
    profile['rows'] = len(df)
    profile['columns'] = len(df.columns)

    # Trend detection (Run on sample)
    trends = detect_trends(sample_df)
    # Correlation matrix (Run on sample)
    correlations = compute_correlations(sample_df)
    # Anomaly detection (Run on sample)
    anomalies = detect_anomalies(sample_df)

    # Combine all insights into a single dict
    summary = {
        "profile": profile,
        "trends": trends,
        "correlations": correlations,
        "anomalies": anomalies,
    }
    # Attach as attribute for easy access in Flask templates
    # Store summary in df.attrs (metadata) to avoid Pandas UserWarning
    df.attrs['profile_summary'] = summary
    return df
