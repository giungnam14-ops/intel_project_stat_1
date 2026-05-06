from flask import Flask, render_template, request, jsonify
from flask_cors import CORS
from data_manager import DataManager
from model_trainer import ModelTrainer
from model_evaluator import ModelEvaluator
from analysis import generate_decision_report, recommend_best_districts, summarize_correlations, generate_reliability_proof
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

def predict_logic(district_name, price):
    print(f"Prediction logic started for: {district_name}, price: {price}")
    
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
    
    # 분석 리포트 생성
    report = generate_decision_report(pred, lower, upper, input_features, rf_model, feature_names, district_name, price)
    
    # 근거 데이터 추가 (피처 중요도)
    importances = []
    if hasattr(rf_model, 'feature_importances_'):
        importances = [
            {"feature": f, "importance": float(i)} 
            for f, i in zip(feature_names, rf_model.feature_importances_)
        ]
        importances = sorted(importances, key=lambda x: x['importance'], reverse=True)[:5]

    # data_manager.py에서 이미 점포당 매출을 3000만~8000만으로 스케일링 완료했으므로,
    # 단순히 점포수로 나누면 현실적인 점포당 예상 매출이 나옵니다.
    store_count = float(sample_row['외식업 점포수'].values[0])
    avg_pred = float(pred) / store_count
    avg_lower = float(lower) / store_count
    avg_upper = float(upper) / store_count

    # 비정형 데이터(리뷰 등) 분석 결과 추가
    unstructured_data = get_unstructured_data(district_name)

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
        "unstructured_data": unstructured_data
    }

@app.route('/api/predict', methods=['POST'])
def predict():
    try:
        data = request.json
        district_name = data.get('district')
        price = data.get('price', 0)
        
        result = predict_logic(district_name, price)
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
        "sales": chart_df['점포당매출'].tolist(),
        "floating": chart_df['총유동'].tolist(),
        "stores": chart_df['외식업 점포수'].tolist(),
        "rent": chart_df['면적당 임대료 (만원)'].tolist()
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)
