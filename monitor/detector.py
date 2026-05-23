import numpy as np
from sklearn.ensemble import IsolationForest
from datetime import datetime

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(
            contamination=0.1,
            random_state=42
        )
        self.is_trained = False
        self.history = []

    def add_sample(self, response_time, status_code):
        self.history.append({
            "response_time": response_time,
            "status_code": status_code,
            "timestamp": datetime.now().isoformat()
        })

    def train(self):
        if len(self.history) < 10:
            return False
        X = np.array([
            [s["response_time"], 1 if s["status_code"] == 200 else 0]
            for s in self.history
        ])
        self.model.fit(X)
        self.is_trained = True
        return True

    def predict(self, response_time, status_code):
        if not self.is_trained:
            return False
        X = np.array([[response_time, 1 if status_code == 200 else 0]])
        result = self.model.predict(X)
        return result[0] == -1

    def get_stats(self):
        if not self.history:
            return {}
        times = [s["response_time"] for s in self.history]
        return {
            "avg_response_time": round(np.mean(times), 2),
            "max_response_time": round(np.max(times), 2),
            "min_response_time": round(np.min(times), 2),
            "total_checks": len(self.history),
            "error_count": sum(1 for s in self.history if s["status_code"] != 200)
        }