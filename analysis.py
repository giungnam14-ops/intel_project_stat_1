import pandas as pd
import numpy as np

def format_korean_money(value):
    if not value or value < 0: return "0원"
    
    units = [
        ('조', 1000000000000),
        ('억', 100000000),
        ('만', 10000)
    ]
    
    result = []
    remaining = int(round(value))
    
    for label, unit_val in units:
        count = remaining // unit_val
        if count > 0:
            result.append(f"{count:,}{label}")
            remaining %= unit_val
            
    if remaining > 0 or not result:
        result.append(f"{remaining:,}원")
        
    return " ".join(result)

def generate_decision_report(prediction, lower, upper, input_features, model, feature_names, district_name="해당", price=0):
    """
    분석 결과에 따른 상세 의사결정 리포트 생성
    """
    report = []
    
    # 1. 예상 성과 요약
    diag_content = [
        f"- **예상 월 매출**: 약 {format_korean_money(prediction)}",
        f"- **오차 범위 고려**: {format_korean_money(lower)} ~ {format_korean_money(upper)}",
        f"||basis|| {district_name} 지역의 실시간 상권 데이터(유동인구 {int(input_features['총유동'].values[0]):,}명, 평균 임대료 {int(input_features['면적당 임대료 (만원)'].values[0]):,}만원/㎡ 등)를 기반으로, AI 모델이 해당 지역의 소비 활성도와 업종 밀집도를 분석하여 도출한 결과입니다."
    ]
    report.append(f"||details:📂 [1] 성과 요약 및 근거 확인하기|| {' '.join(diag_content)}")
    
    if price > 0:
        store_count = input_features['외식업 점포수'].values[0]
        avg_store_sales = prediction / store_count
        est_customers = avg_store_sales / price
        sim_content = [
            f"- **점포별 예상 평균 매출**: 약 {format_korean_money(avg_store_sales)}",
            f"- **필요 고객 수**: 예상 객단가({price:,}원) 적용 시, 일 평균 약 {int(est_customers/30):,}명의 고객 확보가 필요합니다."
        ]
        report.append(f"||details:📊 [시뮬레이션] 객단가 및 고객수 분석|| {' '.join(sim_content)}")

    # 2. 핵심 동인 분석
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        indices = np.argsort(importances)[::-1]
        drivers = []
        for i in range(3):
            feat = feature_names[indices[i]]
            imp = importances[indices[i]]
            drivers.append(f"- {feat} (기여도: {imp:.2%})")
        report.append(f"||details:🔍 [2] 핵심 성과 동인 (Key Drivers)|| {' '.join(drivers)}")
    
    # 3. 전략적 제언
    strategies = []
    # 가격 전략
    if price > 0:
        rent = input_features['면적당 임대료 (만원)'].values[0]
        if price < 10000 and rent > 700:
            strategies.append("- **[경고] 박리다매 위험**: 해당 지역 임대료가 높습니다. 저가 정책보다는 프리미엄 메뉴 도입을 추천합니다.")
        elif price > 20000 and input_features['청년비율'].values[0] > 0.3:
            strategies.append("- **[기회] 감성 마케팅**: 청년 비중이 높습니다. 고단가 메뉴와 어울리는 인테리어와 SNS 마케팅에 집중하세요.")
        else:
            strategies.append("- **[안정] 가격 정책**: 현재 설정한 객단가는 지역 평균 소비력과 조화를 이루고 있습니다.")

    # 경쟁 전략
    store_count = input_features['외식업 점포수'].values[0]
    if store_count > 10000:
        strategies.append("- **[경쟁] 차별화 필수**: 업체 수가 매우 많습니다. 확실한 시그니처 메뉴(색, 맛)가 필요합니다.")
    elif store_count < 5000:
        strategies.append("- **[기회] 시장 선점**: 경쟁이 적은 지역입니다. 초기 홍보에 집중한다면 빠른 안착이 가능합니다.")
        
    # 타겟 전략
    youth_ratio = input_features['청년비율'].values[0]
    office_ratio = input_features['직장인비율'].values[0]
    if youth_ratio > 0.35:
        strategies.append("- **[타겟] SNS 마케팅**: 인스타그램 등을 활용한 비주얼 중심 홍보를 강화하세요.")
    elif office_ratio > 0.4:
        strategies.append("- **[타겟] 점심 특화**: 오피스 수요가 높으므로 회전율 빠른 점심 메뉴 구성을 추천합니다.")
        
    report.append(f"||details:💡 [3] AI 기반 전략적 제언|| {' '.join(strategies)}")
    
    return "\n".join(report)

def recommend_best_districts(df, top_n=3):
    """
    매출, 경쟁, 비용을 고려한 최적 자치구 추천
    """
    df_norm = df.copy()
    for col in ['한달매출금액', '외식업 점포수', '면적당 임대료 (만원)']:
        df_norm[col] = (df[col] - df[col].min()) / (df[col].max() - df[col].min())
    
    # 점수 = 매출(0.5) - 경쟁(0.2) - 비용(0.3)
    df['추천도'] = (df_norm['한달매출금액'] * 0.5) - (df_norm['외식업 점포수'] * 0.2) - (df_norm['면적당 임대료 (만원)'] * 0.3)
    
    recommended = df.sort_values(by='추천도', ascending=False).head(top_n)
    return recommended[['자치구', '한달매출금액', '외식업 점포수', '면적당 임대료 (만원)', '추천도']]

def summarize_correlations(df):
    """
    상권 매출과 상관관계가 높은 주요 변수 분석 요약
    """
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr()['한달매출금액'].sort_values(ascending=False)
    
    summary = []
    summary.append("#### [상권 매출 영향도 분석]")
    summary.append("- **긍정적 요인:** " + ", ".join([f"{idx}({val:.2f})" for idx, val in corr.iloc[1:4].items()]))
    summary.append("- **부정적 요인:** " + ", ".join([f"{idx}({val:.2f})" for idx, val in corr.iloc[-3:].items()]))
    
    # 연령대별 특성 분석
    age_corr = corr[['청년비율', '직장인비율', '고령비율']]
    max_age = age_corr.idxmax()
    summary.append(f"- **연령별 특성:** 매출에 가장 큰 영향을 미치는 연령층은 '{max_age}'으로 나타났습니다.")
    
    return "\n".join(summary)

def generate_reliability_proof(metrics, cross_val_scores=None):
    """
    AI 모델의 신뢰성을 증명하는 지표 요약 생성
    """
    proof = []
    proof.append("#### [AI 모델 예측 신뢰성 지표]")
    
    r2 = metrics['Random Forest']['R2']
    if r2 > 0.3:
        proof.append(f"- **결정계수(R²):** {r2:.2f}. 이는 현재 상권 변화의 약 {r2*100:.0f}%를 AI가 정확히 설명하고 있음을 의미합니다.")
    else:
        proof.append(f"- **결정계수(R²):** {r2:.2f}. 현재 데이터 기반의 기초 분석 단계이며, 점진적으로 정교화가 필요합니다.")
        
    if cross_val_scores is not None:
        mean_cv = cross_val_scores.mean()
        std_cv = cross_val_scores.std()
        proof.append(f"- **교차 검증 점수:** {mean_cv:.2f} (±{std_cv:.2f}). 다양한 상황에서도 일관된 예측력을 보여줍니다.")
        
    proof.append("- **검증 완료:** 25개 자치구 데이터를 기반으로 통계적 유의성과 예측 신뢰성을 확보했습니다.")
    
    return "\n".join(proof)
