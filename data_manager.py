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
        
        # 점포당 평균 매출 (간접 경쟁 지표)
        self.df['점포당매출'] = self.df['한달매출금액'] / self.df['외식업 점포수']
        
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
