import pandas as pd
from preprocessing import load_and_preprocess_data
from modeling import train_and_evaluate, predict_with_range
from analysis import (generate_decision_report, recommend_best_districts, 
                      summarize_correlations, generate_reliability_proof)
from visualization import (plot_feature_importance, plot_actual_vs_predicted, 
                           plot_district_comparison, plot_correlation_heatmap, 
                           plot_age_group_analysis, plot_residuals)

def main():
    print("=== 외식업 창업 의사결정 지원 시스템 (심층 분석 모드) ===\n")
    
    # 1. 데이터 로드 및 전처리
    X, y, le, df_processed = load_and_preprocess_data('data.xlsx')
    feature_names = X.columns.tolist()
    
    # 2. 모델 학습 및 평가
    lr_model, rf_model, metrics, split_data, cv_scores = train_and_evaluate(X, y)
    X_train, X_test, y_train, y_test = split_data
    
    # 3. 데이터 심층 분석 리포트
    print("--- 데이터 심층 분석 ---")
    corr_summary = summarize_correlations(df_processed)
    print(corr_summary)
    print()
    
    # 4. 모델 신뢰성 검증
    print("--- 모델 신뢰성 검증 ---")
    reliability_proof = generate_reliability_proof(metrics, cv_scores)
    print(reliability_proof)
    print()
    
    # 5. 시각화 자료 생성
    print("시각화 자료 생성 중 (히트맵, 연령대 분석 포함)...")
    plot_feature_importance(rf_model, feature_names)
    plot_actual_vs_predicted(y_test, rf_model.predict(X_test))
    plot_district_comparison(df_processed)
    plot_correlation_heatmap(df_processed)
    plot_age_group_analysis(df_processed)
    plot_residuals(y_test, rf_model.predict(X_test))
    print("시각화 완료 (이미지 파일 저장됨)\n")
    
    # 6. 상권 추천
    print("--- 추천 상권 TOP 3 ---")
    recommendations = recommend_best_districts(df_processed)
    print(recommendations)
    print()
    
    # 7. 사용자 입력 기반 예측 예시 (강남구)
    print("--- 특정 지역 분석 예시 ---")
    sample_input = X.iloc[0:1] 
    district_name = le.inverse_transform([sample_input['자치구_code'].values[0]])[0]
    
    mae = metrics["Random Forest"]["MAE"]
    pred, lower, upper = predict_with_range(rf_model, sample_input, mae)
    
    report = generate_decision_report(pred, lower, upper, sample_input, rf_model, feature_names)
    print(f"분석 지역: {district_name}")
    print(report)

if __name__ == "__main__":
    main()
