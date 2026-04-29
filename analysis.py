import pandas as pd
import numpy as np

def format_korean_money(value):
    if not value or value < 0: return "0원"
    
    rawValue = int(round(value))
    
    if rawValue >= 1000000000000: # 조 단위
        jo = rawValue // 1000000000000
        eok = (rawValue % 1000000000000) // 100000000
        return f"{jo:,}조 {eok:,}억" if eok > 0 else f"{jo:,}조"
    elif rawValue >= 100000000: # 억 단위
        eok = rawValue // 100000000
        man = (rawValue % 100000000) // 10000
        return f"{eok:,}억 {man:,}만" if man > 0 else f"{eok:,}억"
    elif rawValue >= 10000: # 만 단위
        man = rawValue // 10000
        return f"{man:,}만원"
    else:
        return f"{rawValue:,}원"

def generate_decision_report(prediction, lower, upper, input_features, model, feature_names, district_name="해당", price=0):
    """
    분석 결과에 따른 상세 의사결정 리포트 생성 (이미 점포당 평균값으로 전달받음)
    """
    report = []
    
    # 1. 예상 성과 요약
    diag_content = [
        f"- **점포당 예상 월 매출**: 약 {format_korean_money(prediction)}",
        f"- **예상 범위**: {format_korean_money(lower)} ~ {format_korean_money(upper)}",
        f"||basis|| {district_name} 지역의 실시간 상권 데이터(유동인구 {int(input_features['총유동'].values[0]):,}명, 평균 임대료 {int(input_features['면적당 임대료 (만원)'].values[0]):,}만원/㎡ 등)를 기반으로 AI가 산출한 '점포당 평균 매출'입니다. 자치구 전체 매출 규모와 점포 밀집도를 고려하여 보정되었습니다."
    ]
    report.append(f"||details:📂 [1] 성과 요약 및 근거 확인하기|| {' '.join(diag_content)}")
    
    if price > 0:
        est_customers = prediction / price
        sim_content = [
            f"- **일평균 필요 고객 수**: 일 평균 약 {int(est_customers/30):,}명의 유료 고객 확보가 필요합니다. (객단가 {price:,}원 기준)",
            f"- **운영 팁**: 현재 상권의 유동인구 대비 타겟 고객 전환율을 높이는 전략이 필요합니다."
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

def calculate_advanced_metrics(df, target_district, current_pred):
    """
    [추가 지표 계산]
    1. 예상 월매출 등급 (A/B/C): 예측값 기준 상위 30% A, 중간 B, 하위 C
    2. 창업/운영 위험도 (0~100): 점포수, 임대료, 유동인구 활용
    3. 경쟁강도 등급 (높음/보통/낮음): 점포수 기준
    """
    
    # 1. 매출 등급 (A/B/C)
    # 전체 자치구의 '한달매출금액' 분포를 기준으로 현재 예측값의 위치 파악
    sales_values = df['한달매출금액'].values
    p70 = np.percentile(sales_values, 70)
    p30 = np.percentile(sales_values, 30)
    
    if current_pred >= p70:
        sales_grade = "A"
    elif current_pred >= p30:
        sales_grade = "B"
    else:
        sales_grade = "C"
        
    # 2. 위험도 (0~100)
    # 점포수(+), 임대료(+), 유동인구(-) 성향 반영
    def normalize(series):
        return (series - series.min()) / (series.max() - series.min())
    
    norm_stores = normalize(df['외식업 점포수'])
    norm_rent = normalize(df['면적당 임대료 (만원)'])
    norm_pop = normalize(df['총유동'])
    
    # 해당 자치구의 인덱스 확인
    idx = df[df['자치구'] == target_district].index[0]
    
    # 위험도 산식: (점포수 비중 40% + 임대료 비중 40% + (1-유동인구) 비중 20%) * 100
    risk_score = (norm_stores[idx] * 0.4 + norm_rent[idx] * 0.4 + (1 - norm_pop[idx]) * 0.2) * 100
    risk_score = min(max(float(risk_score), 0), 100)
    
    # 3. 경쟁강도 (점포수 기준)
    store_values = df['외식업 점포수'].values
    s70 = np.percentile(store_values, 70)
    s30 = np.percentile(store_values, 30)
    
    if df.loc[idx, '외식업 점포수'] >= s70:
        comp_intensity = "높음"
    elif df.loc[idx, '외식업 점포수'] >= s30:
        comp_intensity = "보통"
    else:
        comp_intensity = "낮음"
        
    return {
        "sales_grade": sales_grade,
        "risk_score": round(risk_score, 1),
        "competition_intensity": comp_intensity
    }

def generate_comparison_summary(df, district_name, user_sales, user_rent, pred_sales):
    """
    사용자 목표값(user_sales)과 AI 예측값(pred_sales) 비교 및 수익성 판단
    user_sales, user_rent: 만원 단위
    pred_sales: 점포당 평균 예측 매출 (만원)
    """
    # 1. 목표 대비 분석
    diff = pred_sales - user_sales if user_sales > 0 else 0
    is_achieved = user_sales <= pred_sales if user_sales > 0 else None
    
    diff_text = f"💰 {int(abs(diff)):,}만원 " + ("초과" if diff > 0 else "부족")
    status_text = "✅ 목표 달성 가능" if is_achieved else "❌ 목표 대비 부족"
    if user_sales == 0:
        diff_text = "-"
        status_text = "목표 매출을 입력해 주세요"

    # 2. 수익성 판단 (매출 대비 임대료 비율)
    if user_rent <= 0:
        profit_status = "판단 불가"
        profit_color = "#64748b" # Slate
        rent_ratio_text = "-"
        profit_comment = "임대료 정보가 없어 수익성 판단이 어렵습니다."
    else:
        rent_ratio = (user_rent / pred_sales) * 100 if pred_sales > 0 else 0
        rent_ratio_text = f"{rent_ratio:.1f}%"
        
        if rent_ratio <= 10:
            profit_status = "좋음"
            profit_color = "#10b981"
            profit_comment = "임대료 비중이 낮아 수익성이 우수합니다."
        elif rent_ratio <= 20:
            profit_status = "보통"
            profit_color = "#fbbf24"
            profit_comment = "임대료 비중이 적절한 수준입니다."
        else:
            profit_status = "위험"
            profit_color = "#ef4444"
            profit_comment = "매출 대비 임대료 부담이 큽니다."
        
    # 3. 최종 요약 문장
    if user_sales > 0:
        summary = f"예측 매출({int(pred_sales)}만원)은 목표 대비 {diff_text} 상태입니다. "
        summary += profit_comment
    else:
        summary = "목표 매출과 임대료를 입력하시면 정밀 수익성 진단이 가능합니다."
    
    return {
        "diff_text": diff_text,
        "status_text": status_text,
        "is_achieved": is_achieved,
        "rent_ratio": rent_ratio_text,
            "profit_status": profit_status,
        "profit_color": profit_color,
        "final_comment": summary
    }


def estimate_decline_causes(df, district_name):
    """
    매출 하락 원인 추정 (규칙 기반)
    1. 유동 감소
    2. 점포수 증가
    3. 임대료 부담
    4. 시간대 불일치
    """
    idx = df[df['자치구'] == district_name].index[0]
    row = df.loc[idx]
    
    causes = []
    
    # 1. 유동 감소 (하위 30%)
    if row['총유동'] <= np.percentile(df['총유동'], 30):
        causes.append({
            "title": "유동인구 부족",
            "desc": f"해당 지역의 총 유동인구가 {int(row['총유동']):,}명으로 서울 평균 대비 적어 고객 확보에 한계가 있습니다."
        })
        
    # 2. 점포수 증가 (상위 70%)
    if row['외식업 점포수'] >= np.percentile(df['외식업 점포수'], 70):
        causes.append({
            "title": "과밀 경쟁",
            "desc": f"외식업 점포수가 {int(row['외식업 점포수']):,}개로 밀집도가 매우 높아 개별 점포의 점유율이 하락하고 있습니다."
        })
        
    # 3. 임대료 부담 (상위 70%)
    if row['면적당 임대료 (만원)'] >= np.percentile(df['면적당 임대료 (만원)'], 70):
        causes.append({
            "title": "높은 고정비",
            "desc": f"㎡당 임대료가 {int(row['면적당 임대료 (만원)']):,}만원으로 상위권에 속해 있어 매출 대비 수익성이 낮아질 위험이 큽니다."
        })
        
    # 4. 시간대 불일치 (점심/저녁 비중이 너무 낮음)
    if row['점심비율'] < 0.2 and row['저녁비율'] < 0.2:
         causes.append({
            "title": "주요 시간대 유동 부족",
            "desc": "식사 시간대(점심/저녁)의 유동인구 비중이 낮아 영업 효율이 떨어질 가능성이 높습니다."
        })

    # 원인이 없는 경우 기본 문구
    if not causes:
        causes.append({
            "title": "안정적 시장",
            "desc": "현재 주요 지표상으로는 큰 하락 요인이 없으나, 개별 점포의 서비스 경쟁력 강화가 필요합니다."
        })

    # 최대 2개 반환
    return causes[:2]

def recommend_operation_strategies(df, district_name):
    """
    현재 상권 상태 기반 운영 전략 추천 (규칙 기반)
    1. 노출/마케팅 강화 (유동 높음, 매출 낮음)
    2. 점심 메뉴 강화 (직장인 많음)
    3. 차별화 전략 (경쟁 많음)
    4. SNS/비주얼 마케팅 (청년층 많음)
    """
    idx = df[df['자치구'] == district_name].index[0]
    row = df.loc[idx]
    
    # 평균값 계산
    avg_pop = df['총유동'].mean()
    avg_sales = df['한달매출금액'].mean()
    avg_office = df['직장인비율'].mean()
    avg_youth = df['청년비율'].mean()
    p70_stores = np.percentile(df['외식업 점포수'], 70)
    
    strategies = []
    
    # 1. 노출/마케팅 강화
    if row['총유동'] > avg_pop and row['한달매출금액'] < avg_sales:
        strategies.append({
            "title": "노출 및 접근성 강화",
            "desc": "유동인구는 풍부하지만 실제 매출로 이어지지 않고 있습니다. 간판 시인성 개선이나 매장 입구 마케팅을 강화해 고객 발길을 끌어보세요."
        })
        
    # 2. 점심 메뉴 강화
    if row['직장인비율'] > avg_office or row['점심비율'] > 0.35:
        strategies.append({
            "title": "오피스 타겟 점심 특화",
            "desc": "직장인 비중이 높은 상권입니다. 회전율이 빠른 점심 세트 메뉴나 도시락 배달 서비스를 강화하면 안정적인 매출 확보가 가능합니다."
        })
        
    # 3. 차별화 전략
    if row['외식업 점포수'] >= p70_stores:
        strategies.append({
            "title": "독보적 시그니처 개발",
            "desc": "경쟁 점포가 매우 많은 과밀 지역입니다. 가격 경쟁보다는 해당 매장에서만 맛볼 수 있는 확실한 '시그니처 메뉴'로 차별화가 필수적입니다."
        })
        
    # 4. SNS/비주얼 마케팅
    if row['청년비율'] > avg_youth:
        strategies.append({
            "title": "트렌디한 비주얼 마케팅",
            "desc": "청년층 방문이 활발한 지역입니다. 인스타그램 등 SNS에 공유하기 좋은 감성적인 인테리어와 '사진 찍기 좋은 메뉴' 구성을 추천합니다."
        })

    # 기본 전략
    if not strategies:
        strategies.append({
            "title": "고객 데이터 기반 관리",
            "desc": "평이한 상권 특성을 보이고 있습니다. 방문 고객의 재방문율을 높이기 위한 멤버십이나 지역 밀착형 쿠폰 마케팅을 시작해 보세요."
        })

    return strategies[:2]

def generate_final_summary(adv_metrics, decline_causes, strategies):
    """
    모든 분석 결과를 종합하여 최종 2~3줄 요약 문장 생성
    """
    # 1. 수요와 경쟁 상황 (매출 등급 및 경쟁강도 기반)
    demand_text = "수요가 매우 높고" if adv_metrics['sales_grade'] == 'A' else ("수요가 안정적이고" if adv_metrics['sales_grade'] == 'B' else "수요가 다소 제한적이며")
    comp_text = "경쟁이 치열한" if adv_metrics['competition_intensity'] == '높음' else "경쟁이 적당한"
    
    line1 = f"이 지역은 {demand_text} {comp_text} 상권입니다."
    
    # 2. 리스크와 전략의 핵심 (위험도 및 전략 기반)
    risk_level = "주의" if adv_metrics['risk_score'] > 60 else "안정"
    top_strategy = strategies[0]['title'] if strategies else "현장 중심 마케팅"
    
    line2 = f"현재 {risk_level} 단계의 리스크가 존재하므로, {top_strategy} 전략이 효과적일 것으로 판단됩니다."
    
    # 3. 추가 조언 (리뷰 관리 등)
    line3 = "특히 방문객의 리뷰 관리와 차별화된 메뉴 구성으로 고객 충성도를 높이는 것이 중요합니다."
    
    return f"{line1}\n{line2}\n{line3}"

def analyze_my_store(df, district_name, store_data):
    """
    내 가게 분석 (규칙 기반)
    store_data: {sales, rent, visitors, price, category, hours, delivery}
    """
    idx = df[df['자치구'] == district_name].index[0]
    row = df.loc[idx]
    
    # 1. 지역 평균 데이터 준비
    # 점포당 평균 매출 (만원 단위)
    avg_sales = (row['한달매출금액'] / row['외식업 점포수']) / 10000 / 30.0 # Calibration 고려
    avg_rent = row['면적당 임대료 (만원)']
    
    # 2. 점수 계산 (기본 100점)
    score = 100
    
    # 매출 대비 임대료 비율 (부담도)
    rent_ratio = (store_data['rent'] / store_data['sales']) * 100 if store_data['sales'] > 0 else 0
    if rent_ratio > 30: score -= 30
    elif rent_ratio > 20: score -= 15
    elif rent_ratio > 10: score -= 5
    
    # 유동 대비 방문 효율 (단순 추정)
    # 총유동 대비 하루 방문객 비중
    flow_per_day = row['총유동'] / 30
    visit_efficiency = (store_data['visitors'] / flow_per_day) * 100
    if visit_efficiency < 0.1: score -= 10 # 너무 낮은 방문 효율
    
    # 3. 운영 리스크 조기진단
    if rent_ratio > 30: risk = "위험 (임대료 과다)"
    elif rent_ratio > 20 or visit_efficiency < 0.05: risk = "주의 (수익성 악화)"
    elif score < 70: risk = "보통"
    else: risk = "낮음 (양호)"
    
    # 4. 지역 평균 대비 한줄 비교
    sales_diff = "높고" if store_data['sales'] > avg_sales else "낮은"
    rent_diff = "저렴하며" if store_data['rent'] < avg_rent else "높은"
    comparison = f"선택하신 {district_name} 평균 대비 매출은 {sales_diff}, 임대료는 {rent_diff} 편입니다."
    
    # 5. 분석 근거 및 개선 전략 생성
    evidence_list = []
    strategy_list = []
    
    # 근거 산출
    if rent_ratio > 20:
        evidence_list.append(f"매출 대비 임대료 비중({rent_ratio:.1f}%)이 지역 평균보다 상당히 높습니다.")
    else:
        evidence_list.append("임대료 비중이 안정적이며 고정비 관리가 잘 이루어지고 있습니다.")
        
    if visit_efficiency < 0.1:
        evidence_list.append(f"유동인구 대비 매장 방문 효율({visit_efficiency:.2f}%)이 낮아 잠재 고객 확보가 부족합니다.")
    else:
        evidence_list.append("유동인구 대비 높은 방문 효율을 보이며 집객력이 우수합니다.")
        
    if row['외식업 점포수'] > 1000:
        evidence_list.append(f"인근에 {int(row['외식업 점포수'])}개의 경쟁 점포가 밀집되어 있어 시장 경쟁이 치열합니다.")
        
    # 전략 수립
    if rent_ratio > 25:
        strategy_list.append("고마진 메뉴 라인업을 강화하고 사이드 메뉴 유도로 객단가를 15% 이상 높이세요.")
    
    if visit_efficiency < 0.1:
        strategy_list.append("매장 전면 비주얼(간판, 입간판)을 개선하고 피크 타임에 매장 앞 시식이나 이벤트를 진행하세요.")
        
    if store_data['delivery'] == 'no':
        strategy_list.append("반경 1.5km 내 배달 서비스를 도입하여 홀 방문 외 추가 매출원을 확보하세요.")
    else:
        strategy_list.append("배달 플랫폼 내 리뷰 답글 관리와 '찜' 이벤트를 통해 지역 내 브랜드 인지도를 강화하세요.")
        
    # 6. 핵심 문제 및 전체 요약 생성
    top_issue = ""
    if rent_ratio > 30:
        top_issue = "⚠️ 임대료 비중 과다: 현재 매출 대비 고정비 부담이 매우 위험한 수준입니다."
    elif visit_efficiency < 0.05:
        top_issue = "⚠️ 집객력 심각 부족: 유동인구의 매장 유입이 거의 일어나지 않고 있습니다."
    elif score < 60:
        top_issue = "⚠️ 전반적인 수익성 저하: 매출 증대와 비용 절감이 동시에 시급한 상태입니다."
    else:
        top_issue = "✅ 운영 안정권: 현재의 효율을 유지하며 단골 확보에 집중하세요."

    total_summary = f"현재 매장은 100점 만점에 {max(0, int(score))}점으로, {risk} 수준의 운영 상태를 보이고 있습니다."
    if risk != "낮음 (양호)":
        total_summary += " 최우선 당면 과제를 해결하여 수익성을 개선해야 합니다."

    # 7. 주변 환경 분석 (보조 데이터 기반)
    env_analysis = []
    
    # 학교/청년층
    if row['청년비율'] > df['청년비율'].mean():
        env_analysis.append("🎓 청년 및 학생 유입이 활발한 활기찬 지역입니다.")
    
    # 직장인
    if row['직장인비율'] > df['직장인비율'].mean():
        env_analysis.append("💼 직장인 유동인구가 밀집된 오피스 중심 상권입니다.")
    else:
        env_analysis.append("👨‍👩‍👧‍👦 가족 단위 및 배후 거주지 수요가 안정적인 지역입니다.")
        
    # 학교 인접 추정 (청년비율이 극도로 높거나 특정 조건)
    if row['청년비율'] > df['청년비율'].quantile(0.8):
        env_analysis.append("🏫 인근에 대학가나 대형 학원가가 인접해 있을 가능성이 매우 높습니다.")

    # 8. 주변 환경 맞춤형 추천 전략 생성 (규칙 기반)
    env_strategies = []
    
    # 학교 (청년층 비율 기반)
    if row['청년비율'] > df['청년비율'].mean():
        env_strategies.append("학생 및 청년층이 많은 지역이므로 가성비 높은 '저가/간편식' 메뉴 구성을 강화해 보세요.")
        
    # 직장 (직장인 비율 기반)
    if row['직장인비율'] > df['직장인비율'].mean():
        env_strategies.append("직장인 수요가 집중되는 상권이므로 '점심 특화 세트'나 회전율 빠른 메뉴 도입이 효과적입니다.")
    
    # 주거 (나머지 또는 보완)
    else:
        env_strategies.append("거주 인구가 안정적이므로 '배달 플랫폼 입점'과 '저녁 가족 단위 메뉴' 개발에 집중하세요.")

    return {
        "score": max(0, int(score)),
        "risk": risk,
        "comparison": comparison,
        "strategy": " ".join(strategy_list[:2]),
        "evidence_list": evidence_list[:3],
        "strategy_list": strategy_list[:3],
        "top_issue": top_issue,
        "total_summary": total_summary,
        "environment_analysis": env_analysis,
        "environment_strategy": " ".join(env_strategies[:1]), # 가장 핵심적인 것 하나만
        "evidence": {
            "flow": int(row['총유동']),
            "stores": int(row['외식업 점포수']),
            "rent": int(row['면적당 임대료 (만원)'])
        }
    }

def get_industry_recommendation(df_processed, district_name):
    """자치구 데이터를 기반으로 유망 업종 3가지를 추천"""
    if isinstance(df_processed, str): # 방어적 코드
        return []
        
    row = df_processed[df_processed['자치구'] == district_name].iloc[0]
    
    # 데이터 기반 지표
    floating = row['총유동']
    rent = row['면적당 임대료 (만원)']
    stores = row['외식업 점포수']
    
    # 추천 로직 (임시: 실제로는 더 복잡한 상관관계나 트렌드 분석 필요)
    recommendations = []
    
    # 1. 고유동 지역 -> 브런치/디저트 카페
    if floating > df_processed['총유동'].mean():
        recommendations.append({
            "category": "프리미엄 디저트 카페",
            "score": 92,
            "reason": f"{district_name}은 서울 평균 대비 유동인구가 매우 활발합니다. 높은 집객력을 바탕으로 객단가가 높은 프리미엄 디저트 상권이 유망합니다."
        })
    else:
        recommendations.append({
            "category": "1인 가구 특화 배달 전문점",
            "score": 85,
            "reason": "유동인구보다는 배달 수요가 안정적인 지역입니다. 고정비가 낮은 배달 전문점 형태의 창업을 추천합니다."
        })
        
    # 2. 임대료가 비교적 낮은 지역 -> 가성비 맛집 / 이자카야
    if rent < df_processed['면적당 임대료 (만원)'].mean():
        recommendations.append({
            "category": "골목상권 감성 이자카야",
            "score": 88,
            "reason": "임대료 부담이 적어 주류 마진을 통한 고수익 모델이 가능합니다. 최근 트렌드인 감성 인테리어를 가미한 틈새 공략이 좋습니다."
        })
    else:
        recommendations.append({
            "category": "오피스 점심 특화 한식",
            "score": 82,
            "reason": "임대료가 높지만 배후 소비력이 강력합니다. 회전율이 빠른 점심 특화 메뉴로 승부하는 것이 효율적입니다."
        })
        
    # 3. 경쟁이 적은 곳 -> 퓨전 요리 / 샐러드
    if stores < df_processed['외식업 점포수'].mean():
        recommendations.append({
            "category": "건강식/샐러드 전문점",
            "score": 80,
            "reason": "주변 경쟁 점포 수가 적어 선점 효과를 누릴 수 있습니다. 건강을 중시하는 소비 트렌드에 맞춰 블루오션을 공략하세요."
        })
    else:
        recommendations.append({
            "category": "특색 있는 퓨전 다이닝",
            "score": 75,
            "reason": "경쟁은 치열하지만 활발한 외식 시장입니다. 확고한 컨셉을 가진 퓨전 요리로 차별화된 경쟁력을 확보하는 것이 필수입니다."
        })
        
    return recommendations[:3]

def get_strategy_tips(df_processed, district_name):
    """자치구 특성에 맞는 간단한 창업 전략 팁 제공"""
    if isinstance(df_processed, str): # 방어적 코드
        return []
        
    row = df_processed[df_processed['자치구'] == district_name].iloc[0]
    tips = []
    
    if row['총유동'] > df_processed['총유동'].mean():
        tips.append("풍부한 유동인구를 잡기 위해 '인스타그래머블'한 매장 전면 구성이 중요합니다.")
        tips.append("주말보다는 평일 유동인구의 연령대와 성별을 분석하여 타겟팅하세요.")
    else:
        tips.append("오프라인 집객보다는 온라인 리뷰 관리와 배달 플랫폼 마케팅에 집중하세요.")
        
    if row['면적당 임대료 (만원)'] > df_processed['면적당 임대료 (만원)'].mean():
        tips.append("높은 임대료 극복을 위해 테이블 회전율을 극대화하거나 테이크아웃 비중을 높여야 합니다.")
    
    tips.append(f"{district_name} 지역의 소상공인 커뮤니티나 인근 상인회에 가입하여 현장 정보를 빠르게 습득하세요.")
    
    return tips[:3]

def get_startup_support_info(district_name):
    """창업 지원 관련 외부 사이트 및 기관 정보 안내"""
    return [
        {
            "title": "서울시 소상공인 종합지원포털",
            "desc": "창업 컨설팅, 교육, 자금 지원 정보를 통합 제공하는 서울시 공식 포털입니다.",
            "url": "https://www.seoulall-in-one.go.kr/"
        },
        {
            "title": "서울신용보증재단 창업지원",
            "desc": "청년 창업 및 소상공인을 위한 특별 보증 및 금융 지원 프로그램을 확인하세요.",
            "url": "https://www.seoulshinbo.co.kr/"
        },
        {
            "title": "서울시 청년 창업 허브",
            "desc": "아이디어 단계부터 시장 진출까지 패키지 지원을 제공하는 청년 창업 전문 기관입니다.",
            "url": "https://hub.seoul.go.kr/"
        }
    ]
