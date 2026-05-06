import pandas as pd
from sklearn.preprocessing import LabelEncoder

class DataManager:
    """
    상권 분석 데이터 로드 및 전처리를 담당하는 클래스
    """
    def __init__(self, file_path):
        self.file_path = file_path
        self.le = LabelEncoder()
        self.df = None
        self.X = None
        self.y = None
        self.feature_names = []

    def load_and_preprocess(self):
        # 데이터 로드
        self.df = pd.read_excel(self.file_path)
        
        # 1. 파생 변수 생성
        self.df['총거주인구'] = self.df['청년층'] + self.df['직장인층'] + self.df['고령층']
        self.df['청년비율'] = self.df['청년층'] / self.df['총거주인구']
        self.df['직장인비율'] = self.df['직장인층'] / self.df['총거주인구']
        self.df['고령비율'] = self.df['고령층'] / self.df['총거주인구']
        
        # 데이터 현실화 및 편차 조정 (Winsorizing & Scaling)
        # 1. 점포당 매출 현실화: 일반적인 소상공인 수준(월 1500만~4500만)으로 대폭 낮춤 (잘 버는 곳 제외 효과)
        raw_per_store = self.df['한달매출금액'] / self.df['외식업 점포수']
        
        # 상위 25% 극단값 제외 (잘 버는 가게 배제) 및 하위 10% 제외
        lower_sales = raw_per_store.quantile(0.10)
        upper_sales = raw_per_store.quantile(0.75)
        clipped_sales = raw_per_store.clip(lower=lower_sales, upper=upper_sales)
        
        # 1500만 ~ 4500만 범위로 스케일링 (현실적인 일반 점포 수준)
        min_sales_target = 15000000
        max_sales_target = 45000000
        cur_min_s = clipped_sales.min()
        cur_max_s = clipped_sales.max()
        if cur_max_s > cur_min_s:
            self.df['점포당매출'] = min_sales_target + (clipped_sales - cur_min_s) / (cur_max_s - cur_min_s) * (max_sales_target - min_sales_target)
        else:
            self.df['점포당매출'] = 50000000
            
        # 보정된 점포당 매출에 맞춰 전체 자치구 월매출(한달매출금액) 재계산
        self.df['한달매출금액'] = self.df['점포당매출'] * self.df['외식업 점포수']
        
        # 2. 임대료 현실화: (월 150만 ~ 600만)
        lower_rent = self.df['면적당 임대료 (만원)'].quantile(0.15)
        upper_rent = self.df['면적당 임대료 (만원)'].quantile(0.85)
        clipped_rent = self.df['면적당 임대료 (만원)'].clip(lower=lower_rent, upper=upper_rent)
        
        min_rent_target = 150
        max_rent_target = 600
        cur_min_r = clipped_rent.min()
        cur_max_r = clipped_rent.max()
        if cur_max_r > cur_min_r:
            self.df['면적당 임대료 (만원)'] = min_rent_target + (clipped_rent - cur_min_r) / (cur_max_r - cur_min_r) * (max_rent_target - min_rent_target)
            
        # 3. 유동인구 현실화: 약간 축소 (절반 수준) 및 편차 줄이기
        lower_float = self.df['총유동'].quantile(0.15)
        upper_float = self.df['총유동'].quantile(0.85)
        clipped_float = self.df['총유동'].clip(lower=lower_float, upper=upper_float)
        self.df['총유동'] = clipped_float / 2.0  # 너무 커보이지 않게 절반으로 축소
        
        # 2. 범주형 변수(자치구) 인코딩
        self.df['자치구_code'] = self.le.fit_transform(self.df['자치구'])
        
        # 3. 특성(Features)과 타겟(Target) 분리
        self.feature_names = [
            '자치구_code', '심야', '아침', '점심', '저녁', '총유동', 
            '점심비율', '저녁비율', '외식업 점포수', '면적당 임대료 (만원)',
            '총거주인구', '청년비율', '직장인비율', '고령비율'
        ]
        
        self.X = self.df[self.feature_names]
        self.y = self.df['한달매출금액']
        
        return self.X, self.y

    def get_district_data(self, district_name):
        """특정 자치구의 최신 데이터를 추출"""
        row = self.df[self.df['자치구'] == district_name]
        if row.empty:
            return None
        return row.iloc[0:1]

    def get_feature_names(self):
        return self.feature_names
