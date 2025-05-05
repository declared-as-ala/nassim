import numpy as np
from tensorflow.keras.models import load_model, Model
from tensorflow.keras.layers import Input, SimpleRNN, Dense
from typing import List, Dict, Any, Optional
from sklearn.preprocessing import MinMaxScaler


class FailurePredictor:
    def __init__(self, model_path: str, seq_len: int, feat_count: int) -> None:
        self.seq_len = seq_len
        self.scaler = MinMaxScaler()
        try:
            self.model = load_model(model_path)
        except OSError:
            inputs = Input(shape=(seq_len, feat_count))
            x = SimpleRNN(16)(inputs)
            outputs = Dense(1, activation="sigmoid")(x)
            model = Model(inputs, outputs)
            model.compile(optimizer="adam", loss="binary_crossentropy")
            self.model = model

    def prepare(self, history: List[Dict[str, Any]]) -> Optional[np.ndarray]:
        if len(history) < self.seq_len:
            return None
        window = history[-self.seq_len :]
        data = [
            [
                d["temperature"],
                d["humidity"],
                d["vibration"],
                d["voltage"],
                d["current"],
            ]
            for d in window
        ]
        arr = self.scaler.fit_transform(data)
        return np.expand_dims(arr, axis=0)

    def predict(self, input_data: Optional[np.ndarray]) -> float:
        if input_data is None:
            return 0.0
        try:
            return float(self.model.predict(input_data)[0][0])
        except Exception:
            return 0.0

    def evaluate(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        risk = self.predict(self.prepare(history))
        status = "CRITIQUE" if risk >= 0.7 else "ATTENTION" if risk >= 0.4 else "OK"
        return {"risk": risk, "motor_status": status}
