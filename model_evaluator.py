import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import cross_val_score

class ModelEvaluator:
    """
    학습된 모델의 성능을 평가하고 검증하는 클래스
    """
    @staticmethod
    def calculate_metrics(y_true, y_pred):
        mae = mean_absolute_error(y_true, y_pred)
        rmse = np.sqrt(mean_squared_error(y_true, y_pred))
        r2 = r2_score(y_true, y_pred)
        return {"MAE": mae, "RMSE": rmse, "R2": r2}

    @staticmethod
    def get_cross_val_scores(model, X, y, cv=3):
        scores = cross_val_score(model, X, y, cv=cv)
        return scores

    def evaluate_all(self, models, split_data):
        X_train, X_test, y_train, y_test = split_data
        all_metrics = {}
        
        for name, model in models.items():
            preds = model.predict(X_test)
            all_metrics[name] = self.calculate_metrics(y_test, preds)
            
        return all_metrics
