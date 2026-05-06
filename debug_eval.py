import sys
import os
import pandas as pd
from preprocessing import load_and_preprocess_data
from modeling import train_and_evaluate

def check_eval():
    try:
        X, y, le, df_processed = load_and_preprocess_data('data.xlsx')
        lr_model, rf_model, metrics, split_data, cv_scores = train_and_evaluate(X, y)
        
        print("\n=== 모델 평가 결과 확인 ===")
        for model_name, score in metrics.items():
            print(f"\n[{model_name}]")
            print(f"  - MAE  : {score['MAE']:,.2f}")
            print(f"  - RMSE : {score['RMSE']:,.2f}")
            print(f"  - R2   : {score['R2']:.4f}")
            
        print(f"\n[Random Forest 교차 검증]")
        print(f"  - 평균 점수: {cv_scores.mean():.4f}")
        print(f"  - 표준 편차: {cv_scores.std():.4f}")
        
    except Exception as e:
        print(f"에러 발생: {e}")

if __name__ == "__main__":
    check_eval()
