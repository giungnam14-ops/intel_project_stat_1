import pandas as pd
import json

try:
    df = pd.read_excel('data.xlsx')
    info = {
        "columns": df.columns.tolist(),
        "shape": df.shape,
        "head": df.head(10).to_dict(orient='records'),
        "dtypes": df.dtypes.astype(str).to_dict(),
        "summary": df.describe(include='all').to_dict()
    }
    print(json.dumps(info, indent=2, default=str))
except Exception as e:
    print(f"Error: {e}")
