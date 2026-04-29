import pandas as pd

try:
    df = pd.read_excel('data.xlsx')
    print("Unique districts in data.xlsx:")
    print(df['자치구'].unique())
    
    target = '성북구'
    if target in df['자치구'].unique():
        print(f"\nFound '{target}' exactly.")
    else:
        print(f"\nCould not find '{target}' exactly.")
        # Check for similar names
        matches = [d for d in df['자치구'].unique() if target in str(d) or str(d) in target]
        if matches:
            print(f"Similar matches: {matches}")
except Exception as e:
    print(f"Error reading data.xlsx: {e}")
