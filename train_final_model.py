"""Train the final Random Forest on all 120 observations and save it for the platform."""
import json
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import GridSearchCV, train_test_split

TARGET = "Undernourishment_pct_final"
PREDICTORS = ["Rainfall_mm", "Temperature_C", "GDP_per_capita_USD",
              "Inflation_pct", "Poverty_rate_interpolated", "Agri_value_added_pctGDP"]

data = pd.read_csv("data/final_panel_dataset.csv")
X, y = data[PREDICTORS], data[TARGET]

# Step 1: choose the hyperparameters on the training set only (same design as Chapter 4)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
grid = {"n_estimators": [200, 500], "max_depth": [None, 5, 10],
        "min_samples_leaf": [1, 3, 5], "max_features": ["sqrt", 1.0]}
search = GridSearchCV(RandomForestRegressor(random_state=42, n_jobs=-1), grid, cv=5,
                      scoring="neg_root_mean_squared_error", n_jobs=-1).fit(X_train, y_train)
best_params = search.best_params_
print("Best hyperparameters:", best_params)
print("Cross-validated RMSE on the training set:", round(-search.best_score_, 3))

# Step 2: honest performance estimate on the 20% that the search never saw
predicted = search.best_estimator_.predict(X_test)
test_metrics = {"RMSE": float(np.sqrt(mean_squared_error(y_test, predicted))),
                "MAE": float(mean_absolute_error(y_test, predicted)),
                "R2": float(r2_score(y_test, predicted))}
print("Test metrics (random split):", {k: round(v, 3) for k, v in test_metrics.items()})

# Step 3: refit the final model on all 120 observations with those hyperparameters
final_model = RandomForestRegressor(random_state=42, n_jobs=-1, **best_params).fit(X, y)

# Step 4: save the model and its description
Path("model").mkdir(exist_ok=True)
joblib.dump(final_model, "model/final_random_forest.joblib")
metadata = {
    "trained_on": str(date.today()),
    "scikit_learn_version": sklearn.__version__,
    "n_observations": int(len(data)),
    "predictors": PREDICTORS,
    "hyperparameters": {k: (None if v is None else v) for k, v in best_params.items()},
    "test_metrics_random_split": test_metrics,
    "temporal_test_r2": 0.143,
    "predictor_ranges": {c: [float(data[c].min()), float(data[c].max())] for c in PREDICTORS},
}
with open("model/model_info.json", "w", encoding="utf-8") as f:
    json.dump(metadata, f, indent=2)
print("Saved: model/final_random_forest.joblib and model/model_info.json")