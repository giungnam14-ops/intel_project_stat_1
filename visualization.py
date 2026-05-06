import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 한글 폰트 설정 (Windows 기준)
plt.rcParams['font.family'] = 'Malgun Gothic'
plt.rcParams['axes.unicode_minus'] = False

def plot_feature_importance(model, feature_names, save_path='feature_importance.png'):
    if hasattr(model, 'feature_importances_'):
        importances = model.feature_importances_
        indices = np.argsort(importances)
        
        plt.figure(figsize=(10, 8))
        plt.title('변수 중요도 (Random Forest)')
        plt.barh(range(len(indices)), importances[indices], align='center')
        plt.yticks(range(len(indices)), [feature_names[i] for i in indices])
        plt.xlabel('상대적 중요도')
        plt.tight_layout()
        plt.savefig(save_path)
        plt.close()

def plot_actual_vs_predicted(y_true, y_pred, save_path='actual_vs_predicted.png'):
    plt.figure(figsize=(8, 6))
    plt.scatter(y_true, y_pred, alpha=0.5)
    plt.plot([y_true.min(), y_true.max()], [y_true.min(), y_true.max()], 'r--', lw=2)
    plt.xlabel('실제 매출')
    plt.ylabel('예측 매출')
    plt.title('실제 vs 예측 매출 비교')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def plot_district_comparison(df, save_path='district_comparison.png'):
    top_districts = df.sort_values(by='한달매출금액', ascending=False).head(10)
    
    plt.figure(figsize=(12, 6))
    sns.barplot(data=top_districts, x='자치구', y='한달매출금액')
    plt.title('서울시 자치구별 월 매출 상위 10개 지역')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def plot_correlation_heatmap(df, save_path='correlation_heatmap.png'):
    plt.figure(figsize=(12, 10))
    # 수치형 데이터만 선택
    numeric_df = df.select_dtypes(include=[np.number])
    corr = numeric_df.corr()
    sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f", linewidths=0.5)
    plt.title('데이터 변수 간 상관관계 히트맵')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def plot_age_group_analysis(df, save_path='age_group_analysis.png'):
    age_cols = ['청년비율', '직장인비율', '고령비율']
    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    
    for i, col in enumerate(age_cols):
        sns.regplot(data=df, x=col, y='한달매출금액', ax=axes[i])
        axes[i].set_title(f'{col} vs 매출 상관관계')
        
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()

def plot_residuals(y_true, y_pred, save_path='residuals_analysis.png'):
    residuals = y_true - y_pred
    plt.figure(figsize=(10, 6))
    sns.scatterplot(x=y_pred, y=residuals)
    plt.axhline(y=0, color='r', linestyle='--')
    plt.xlabel('예측 매출')
    plt.ylabel('잔차 (실제 - 예측)')
    plt.title('모델 신뢰성 검증: 잔차 분석 차트')
    plt.tight_layout()
    plt.savefig(save_path)
    plt.close()
