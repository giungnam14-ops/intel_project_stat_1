import pandas as pd
import numpy as np

all_districts = [
    '강남구', '강동구', '강북구', '강서구', '관악구', '광진구', '구로구', '금천구', '노원구', '도봉구', 
    '동대문구', '동작구', '마포구', '서대문구', '서초구', '성동구', '성북구', '송파구', '양천구', '영등포구', 
    '용산구', '은평구', '종로구', '중구', '중랑구'
]

try:
    df = pd.read_excel('data.xlsx')
    existing_districts = df['자치구'].unique().tolist()
    
    missing = [d for d in all_districts if d not in existing_districts]
    
    if missing:
        print(f"Missing districts: {missing}")
        
        # Calculate mean for numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        means = df[numeric_cols].mean()
        
        new_rows = []
        for d in missing:
            new_row = means.copy()
            new_row['자치구'] = d
            new_rows.append(new_row)
            
        df_new = pd.DataFrame(new_rows)
        df_final = pd.concat([df, df_new], ignore_index=True)
        
        # Save back to Excel
        df_final.to_excel('data.xlsx', index=False)
        print("Successfully added missing districts to data.xlsx")
    else:
        print("No districts missing.")
        
except Exception as e:
    print(f"Error: {e}")
