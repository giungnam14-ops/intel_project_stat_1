from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor

class ModelTrainer:
    """
    AI 상권 분석 모델 학습을 담당하는 클래스
    """
    def __init__(self, random_state=42):
        self.random_state = random_state
        self.models = {}
        self.split_data = None

    def train_models(self, X, y):
        # 데이터셋 분리
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=self.random_state
        )
        self.split_data = (X_train, X_test, y_train, y_test)
        
        # 1. Linear Regression (Baseline)
        lr_model = LinearRegression()
        lr_model.fit(X_train, y_train)
        self.models['Linear Regression'] = lr_model
        
        # 2. Random Forest (Main Model)
        rf_model = RandomForestRegressor(n_estimators=100, random_state=self.random_state)
        rf_model.fit(X_train, y_train)
        self.models['Random Forest'] = rf_model
        
        return self.models, self.split_data

    def predict_with_range(self, model_name, input_data, mae):
        """
        예측값과 오차 범위를 반환
        """
        model = self.models.get(model_name)
        if not model:
            return None
            
        prediction = model.predict(input_data)[0]
        lower_bound = prediction - mae
        upper_bound = prediction + mae
        
        return prediction, lower_bound, upper_bound
