import pandas as pd
import numpy as np

def prepare_chart_data(df: pd.DataFrame, summary: dict) -> dict:
    """
    Prepare data for Chart.js visualizations (KPIs, Trends, Bar, Heatmap, Scatter).
    """
    charts = {}

    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    # 1. KPI Data
    # Calculate missing percentage
    total_cells = df.size
    total_missing = df.isnull().sum().sum()
    missing_pct = (total_missing / total_cells) * 100 if total_cells > 0 else 0
    
    # Calculate anomaly count (if available in summary)
    anomaly_count = 0
    if summary and 'anomalies' in summary:
         for idx_list in summary['anomalies'].values():
             anomaly_count += len(idx_list)
    anomaly_pct = (anomaly_count / len(df)) * 100 if len(df) > 0 else 0

    charts['kpi'] = {
        'rows': len(df),
        'columns': len(df.columns),
        'missing_count': int(total_missing), # int for JSON serialization
        'missing_pct': round(missing_pct, 1),
        'anomaly_count': anomaly_count,
        'anomaly_pct': round(anomaly_pct, 1)
    }

    # 2. Trend Line Chart (Revenue Over Time)
    # Pick the numeric column with highest variance as "Metric"
    metric_col = None
    if numeric_cols:
        variances = df[numeric_cols].var()
        metric_col = variances.idxmax()
    
    if metric_col:
        # Downsample for chart if too big (max 50 points)
        if len(df) > 50:
            df_chart = df.iloc[::len(df)//50, :]
        else:
            df_chart = df
            
        charts['trend'] = {
            'label': metric_col,
            'labels': df_chart.index.tolist(),
            'data': df_chart[metric_col].fillna(0).tolist()
        }

    # 3. Bar Chart (Category Comparison)
    # Pick a categorical col with 3-15 unique values
    cat_col = None
    if categorical_cols:
        for col in categorical_cols:
            n_unique = df[col].nunique()
            if 3 <= n_unique <= 15:
                cat_col = col
                break
    
    if cat_col and metric_col:
        # Aggregate metric by category
        grouped = df.groupby(cat_col)[metric_col].sum().sort_values(ascending=False).head(10)
        charts['bar'] = {
            'label': f"{metric_col} by {cat_col}",
            'labels': grouped.index.astype(str).tolist(),
            'data': grouped.values.tolist()
        }

    # 4. Correlation Heatmap
    # We need labels (x/y) and data points (x, y, v)
    if len(numeric_cols) > 1:
        corr = df[numeric_cols].corr()
        heatmap_data = []
        for i, row_col in enumerate(corr.columns):
            for j, col_col in enumerate(corr.columns):
                heatmap_data.append({'x': row_col, 'y': col_col, 'v': round(corr.iloc[i, j], 2)})
        
        charts['heatmap'] = {
            'labels': corr.columns.tolist(),
            'data': heatmap_data
        }

    # 5. Anomaly Scatter
    # Plot two numeric variables against each other, highlight anomalies
    if len(numeric_cols) >= 2:
        x_col = numeric_cols[0]
        y_col = numeric_cols[1]
        
        # Determine anomaly indices
        anomaly_indices = set()
        if summary and 'anomalies' in summary:
             for idx_list in summary['anomalies'].values():
                 anomaly_indices.update(idx_list)
        
        normal_data = []
        anomaly_data = []
        
        # Sample if too large (max 200 points) to avoid lag
        sample_df = df.head(200)
        
        for idx, row in sample_df.iterrows():
            point = {'x': row[x_col], 'y': row[y_col]}
            if idx in anomaly_indices:
                anomaly_data.append(point)
            else:
                normal_data.append(point)

        charts['scatter'] = {
            'x_label': x_col,
            'y_label': y_col,
            'normal': normal_data,
            'anomalies': anomaly_data
        }

    return charts
