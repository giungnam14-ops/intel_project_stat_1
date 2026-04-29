from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from data_manager import DataManager
from model_trainer import ModelTrainer
from model_evaluator import ModelEvaluator
from analysis import (
    generate_decision_report, recommend_best_districts, summarize_correlations, 
    generate_reliability_proof, calculate_advanced_metrics, generate_comparison_summary, 
    estimate_decline_causes, recommend_operation_strategies, generate_final_summary, 
    analyze_my_store, get_industry_recommendation, get_strategy_tips, get_startup_support_info
)
from nlp_mock_data import get_unstructured_data

app = Flask(__name__)
CORS(app)

# 1. 데이터 관리자 초기화 및 로드
dm = DataManager('data.xlsx')
X, y = dm.load_and_preprocess()
df_processed = dm.df
feature_names = dm.get_feature_names()

# 2. 모델 학습 및 평가 초기화
trainer = ModelTrainer()
models, split_data = trainer.train_models(X, y)
rf_model = models['Random Forest']

evaluator = ModelEvaluator()
metrics = evaluator.evaluate_all(models, split_data)
cv_scores = evaluator.get_cross_val_scores(rf_model, X, y)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/districts', methods=['GET'])
def get_districts():
    districts = df_processed['자치구'].unique().tolist()
    return jsonify(districts)

@app.route('/api/summary', methods=['GET'])
def get_summary():
    # 상위 추천 지역 TOP 3
    recommendations = recommend_best_districts(df_processed, top_n=5)
    
    # 모델 성능 요약
    perf = {
        "mae": float(metrics["Random Forest"]["MAE"]),
        "r2": float(metrics["Random Forest"]["R2"]),
        "cv_mean": float(cv_scores.mean())
    }
    
    # 간단한 상관관계 요약
    corr_summary = summarize_correlations(df_processed)
    
    return jsonify({
        "recommendations": recommendations.to_dict(orient='records'),
        "performance": perf,
        "insights": corr_summary
    })

def predict_logic(district_name, price, user_sales=0, user_rent=0):
    print(f"Prediction logic started for: {district_name}, price: {price}, user_sales: {user_sales}, user_rent: {user_rent}")
    
    if not district_name:
        raise ValueError("자치구를 지정해 주세요.")

    # 해당 자치구의 데이터 추출
    sample_row = dm.get_district_data(district_name)
    
    if sample_row is None:
        raise ValueError(f"'{district_name}' 데이터를 찾을 수 없습니다.")
    
    # 모델 학습 시 사용된 피처만 선택
    input_features = sample_row[feature_names]
    
    # 예측 수행
    mae = metrics["Random Forest"]["MAE"]
    pred, lower, upper = trainer.predict_with_range("Random Forest", input_features, mae)
    
    # [수정] 자치구 총 매출이 아닌 점포당 평균 매출로 모든 분석 수행
    # 외식업 통계청 평균 매출 데이터 스케일에 맞춘 보정 계수(Calibration Factor) 적용
    CALIBRATION_FACTOR = 30.0
    store_count = float(sample_row['외식업 점포수'].values[0])
    
    avg_pred = (float(pred) / store_count) / CALIBRATION_FACTOR
    avg_lower = (float(lower) / store_count) / CALIBRATION_FACTOR
    avg_upper = (float(upper) / store_count) / CALIBRATION_FACTOR

    # 분석 리포트 생성 (이제 avg_pred 등을 전달)
    report = generate_decision_report(avg_pred, avg_lower, avg_upper, input_features, rf_model, feature_names, district_name, price)
    
    # 근거 데이터 추가 (피처 중요도)
    importances = []
    if hasattr(rf_model, 'feature_importances_'):
        importances = [
            {"feature": f, "importance": float(i)} 
            for f, i in zip(feature_names, rf_model.feature_importances_)
        ]
        importances = sorted(importances, key=lambda x: x['importance'], reverse=True)[:5]

    # 비정형 데이터(리뷰 등) 분석 결과 추가
    unstructured_data = get_unstructured_data(district_name)

    # 추가 지표 계산 (매출 등급, 위험도, 경쟁강도)
    advanced_metrics = calculate_advanced_metrics(df_processed, district_name, float(pred))

    # 사용자 입력값 대비 비교 요약 생성 (avg_pred 전달)
    comparison_summary = generate_comparison_summary(df_processed, district_name, user_sales, user_rent, avg_pred)

    # 매출 하락 원인 추정
    decline_causes = estimate_decline_causes(df_processed, district_name)

    # 운영 전략 추천
    strategies = recommend_operation_strategies(df_processed, district_name)

    # 최종 종합 요약 생성
    final_summary = generate_final_summary(advanced_metrics, decline_causes, strategies)

    # 추천 업종, 전략 팁, 창업 지원 정보 추가
    industry_recs = get_industry_recommendation(df_processed, district_name)
    strategy_tips = get_strategy_tips(df_processed, district_name)
    support_info = get_startup_support_info(district_name)

    return {
        "prediction": avg_pred,
        "lower": avg_lower,
        "upper": avg_upper,
        "total_prediction": float(pred),
        "store_count": store_count,
        "report": report,
        "district": district_name,
        "price": price,
        "evidence": {
            "importances": importances
        },
        "unstructured_data": unstructured_data,
        "advanced_metrics": advanced_metrics,
        "comparison_summary": comparison_summary,
        "decline_causes": decline_causes,
        "operation_strategies": strategies,
        "final_summary": final_summary,
        "industry_recommendations": industry_recs,
        "strategy_tips": strategy_tips,
        "startup_support": support_info
    }

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        district_name = data.get('district')
        price = data.get('price', 0)
        user_sales = data.get('user_sales', 0)
        user_rent = data.get('user_rent', 0)
        
        result = predict_logic(district_name, price, user_sales, user_rent)
        return jsonify(result)
    except Exception as e:
        import traceback
        print("ERROR in /api/predict:")
        print(traceback.format_exc())
        return jsonify({"error": str(e)}), 500

@app.route('/api/chart-data', methods=['GET'])
def get_chart_data():
    # 차트용 데이터 (전체 자치구 지표 비교)
    chart_df = df_processed.copy()
    return jsonify({
        "labels": chart_df['자치구'].tolist(),
        "sales": chart_df['한달매출금액'].tolist(),
        "floating": chart_df['총유동'].tolist(),
        "stores": chart_df['외식업 점포수'].tolist(),
        "rent": chart_df['면적당 임대료 (만원)'].tolist()
    })

@app.route('/api/analyze-mystore', methods=['POST'])
def analyze_mystore_api():
    try:
        data = request.json
        district_name = data.get('district')
        store_data = data.get('store_data')
        
        if not district_name:
            return jsonify({"error": "먼저 지도를 클릭하여 분석할 자치구를 선택해 주세요."}), 400
            
        result = analyze_my_store(df_processed, district_name, store_data)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)
