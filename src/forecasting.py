"""
FinMatrix Dynamic Time-Series Forecasting Engine
Ensembled Random Forest model with temporal holdout lag features (t-1, t-7).
Dynamically retrains on custom uploaded SME datasets.
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor


class CashFlowForecaster:
    def __init__(self):
        self.model = RandomForestRegressor(n_estimators=100, random_state=42)

    def prepare_lag_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Generates lag-1 and lag-7 temporal features from net_flow series.
        """
        data = df.copy()
        if 'net_flow' not in data.columns and 'inflow' in data.columns and 'outflow' in data.columns:
            data['net_flow'] = data['inflow'] - data['outflow']

        data['lag_1'] = data['net_flow'].shift(1)
        data['lag_7'] = data['net_flow'].shift(7)
        data['rolling_7_mean'] = data['net_flow'].shift(1).rolling(window=7).mean()

        return data.dropna().reset_index(drop=True)

    def predict_next_days(self, df: pd.DataFrame, days: int = 30) -> pd.DataFrame:
        """
        Trains model on provided historical dataframe and projects future net cash flows.
        Guarantees zero random number fallback.
        """
        
        # Validate forecast horizon.
        if isinstance(days, bool) or not isinstance(days, (int, np.integer)) or days <= 0:
            raise ValueError("days must be a positive integer.")

        # Validate historical input.
        if df is None or not isinstance(df, pd.DataFrame) or df.empty:
            raise ValueError("Historical data must be a non-empty pandas DataFrame.")

        if len(df) < 14:
            raise ValueError(
                "Insufficient historical records. Minimum 14 records required."
            )

        # Require a supported date column.
        date_col = next(
            (col for col in ["trans_date", "date"] if col in df.columns),
            None,
        )
        if date_col is None:
            raise ValueError(
                "Missing date column. Expected 'trans_date' or 'date'."
            )

        if "net_flow" not in df.columns:
            if {"inflow", "outflow"}.issubset(df.columns):
                df = df.copy()
                df["net_flow"] = (
                    pd.to_numeric(df["inflow"], errors="coerce")
                    - pd.to_numeric(df["outflow"], errors="coerce")
                )
            else:
                raise ValueError(
                    "Missing net_flow. Provide net_flow or both inflow and outflow."
                )

        data = df.copy()
        data["trans_date"] = pd.to_datetime(data[date_col], errors="coerce")

        if data["trans_date"].isna().any():
            raise ValueError("Historical data contains invalid or missing dates.")

        data["net_flow"] = pd.to_numeric(data["net_flow"], errors="coerce")

        if not np.isfinite(data["net_flow"].to_numpy(dtype=float)).all():
            raise ValueError(
                "net_flow must contain only finite numeric values; missing, "
                "infinite, or non-numeric values are not allowed."
            )

        data = (
            data.sort_values("trans_date")
            .reset_index(drop=True)
        )
 
        featured_df = self.prepare_lag_features(data)

        if len(featured_df) < 7:
            raise ValueError("Dataset too short after generating temporal lag features.")

        X = featured_df[['lag_1', 'lag_7', 'rolling_7_mean']]
        y = featured_df['net_flow']

        self.model.fit(X, y)

        last_date = data['trans_date'].iloc[-1] if 'trans_date' in data.columns else pd.Timestamp.today()
        future_dates = pd.date_range(start=last_date + pd.Timedelta(days=1), periods=days, freq='D')

        predictions = []
        recent_history = list(data['net_flow'].values[-14:])

        for _ in range(days):
            lag_1 = recent_history[-1]
            lag_7 = recent_history[-7]
            rolling_mean = np.mean(recent_history[-7:])

            feat_vector = pd.DataFrame(
    [[lag_1, lag_7, rolling_mean]],
    columns=['lag_1', 'lag_7', 'rolling_7_mean']
)
            pred_val = float(self.model.predict(feat_vector)[0])

            predictions.append(pred_val)
            recent_history.append(pred_val)

        forecast_df = pd.DataFrame({
            "Date": future_dates,
            "Predicted_Net_Flow": predictions
        })

        return forecast_df