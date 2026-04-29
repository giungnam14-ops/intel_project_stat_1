import pandas as pd
import sys

# Ensure UTF-8 output for console
sys.stdout.reconfigure(encoding='utf-8')

try:
    df = pd.read_excel('data.xlsx')
    districts = df['자치구'].unique()
    print("Districts in data.xlsx:")
    for d in districts:
        print(f"'{d}' (Length: {len(str(d))})")
    
    target = '성북구'
    found = False
    for d in districts:
        if str(d).strip() == target:
            print(f"\nMatch found for '{target}' after stripping.")
            found = True
            break
        if target in str(d):
            print(f"\nPartial match found: '{d}' contains '{target}'")
            found = True
            break
            
    if not found:
        print(f"\nNo match found for '{target}'.")

except Exception as e:
    print(f"Error: {e}")
