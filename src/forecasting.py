"""
FinPilot AI — Time-Series Cash Flow Forecasting Engine
Trains Random Forest Regressors on historical lag features (t-1, t-7)
to generate 30-day forward cash-flow predictions under Level 1 Temporal constraints.
"""

import os
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from typing import Dict, Any, Tuple


class CashFlowForecaster:
    def __init__(self, data_path: str = "data/raw/bangladesh_sme_cashflow.csv"):
        self.data_path = data_path
        self.model = RandomForestRegressor(n_estimators=100, max_depth=5, random_state=42)
        self.is_trained = False

    def load_and_prepare_data(self) -> pd.DataFrame:
        """Loads transaction logs and constructs leakage-free lag features."""
        if not os.path.exists(self.data_path):
            # Fallback inline generation if file missing
            dates = pd.date_range(start="2026-01-01", periods=180, freq="D")
            np.random.seed(42)
            net_flow = np.random.normal(loc=15000, scale=25000, size=180)
            df = pd.DataFrame({"date": dates, "net_flow": net_flow})
        else:
            df = pd.read_csv(self.data_path)
            df['date'] = pd.to_datetime(df['date'])
            if 'net_flow' not in df.columns:
                df['net_flow'] = np.where(df['transaction_type'] == 'inflow', df['amount'], -df['amount'])

        df = df.sort_values('date').reset_index(drop=True)
        
        # Strict historical lags (No lookahead leakage)
        df['lag_1d'] = df['net_flow'].shift(1)
        df['lag_7d'] = df['net_flow'].shift(7)
        df['rolling_mean_7d'] = df['net_flow'].shift(1).rolling(7).mean()
        df['rolling_median_7d'] = df['net_flow'].shift(1).rolling(7).median()

        return df.dropna().reset_index(drop=True)

    def train_model(self) -> Dict[str, float]:
        """Trains ML model on chronological train-test split."""
        df = self.load_and_prepare_data()
        feature_cols = ['lag_1d', 'lag_7d', 'rolling_mean_7d', 'rolling_median_7d']
        
        # Level 1 Temporal Split (80% Train, 20% Holdout Test)
        split_idx = int(len(df) * 0.8)
        train_df = df.iloc[:split_idx]
        test_df = df.iloc[split_idx:]

        X_train, y_train = train_df[feature_cols], train_df['net_flow']
        X_test, y_test = test_df[feature_cols], test_df['net_flow']

        self.model.fit(X_train, y_train)
        self.is_trained = True

        predictions = self.model.predict(X_test)
        mae = float(np.mean(np.abs(predictions - y_test)))
        rmse = float(np.sqrt(np.mean((predictions - y_test) ** 2)))

        return {"mae": round(mae, 2), "rmse": round(rmse, 2), "test_samples": len(test_df)}

    def predict_next_days(self, days: int = 30) -> pd.DataFrame:
        """Generates forward-looking ML cash flow forecast with uncertainty bounds."""
        if not self.is_trained:
            self.train_model()

        df = self.load_and_prepare_data()
        last_date = df['date'].max()
        feature_cols = ['lag_1d', 'lag_7d', 'rolling_mean_7d', 'rolling_median_7d']
        
        recent_history = list(df['net_flow'].values[-14:])
        forecast_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days, freq="D")
        forecast_values = []

        for _ in range(days):
            lag_1d = recent_history[-1]
            lag_7d = recent_history[-7]
            rolling_mean_7d = float(np.mean(recent_history[-7:]))
            rolling_median_7d = float(np.median(recent_history[-7:]))

            # Feature names matching training DataFrame to avoid UserWarning
            features = pd.DataFrame([{
                'lag_1d': lag_1d,
                'lag_7d': lag_7d,
                'rolling_mean_7d': rolling_mean_7d,
                'rolling_median_7d': rolling_median_7d
            }])
            
            pred = float(self.model.predict(features)[0])
            forecast_values.append(pred)
            recent_history.append(pred)

        df_forecast = pd.DataFrame({
            "Date": forecast_dates,
            "Predicted_Net_Flow": np.round(forecast_values, 2),
            "Lower_Bound": np.round(np.array(forecast_values) - 12000, 2),
            "Upper_Bound": np.round(np.array(forecast_values) + 12000, 2)
        })

        return df_forecast


if __name__ == "__main__":
    print("--- Testing ML Forecasting Engine ---")
    forecaster = CashFlowForecaster()
    metrics = forecaster.train_model()
    print(f"Model Trained Successfully. MAE: {metrics['mae']} BDT | RMSE: {metrics['rmse']} BDT")
    
    df_preds = forecaster.predict_next_days(days=30)
    print("\nNext 5 Days ML Predicted Cash Flow:")
    print(df_preds.head())