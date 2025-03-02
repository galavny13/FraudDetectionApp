# app/ml/train_model.py
import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split, RandomizedSearchCV
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, f1_score
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline

def load_data(csv_path="app/ml/credit_card_transactions.csv"):
    """
    1) Load CSV
    2) Parse trans_date_trans_time
    3) Create hour, day_of_week
    4) Compute naive distance (fill missing lat/long with 0, so we don't drop rows)
    5) Keep relevant columns only
    """

    # 1) Load
    df = pd.read_csv(csv_path)
    print("Initial CSV shape:", df.shape)

    # 2) Parse datetime (your data is YYYY-MM-DD HH:MM:SS)
    df["trans_date_trans_time"] = pd.to_datetime(
        df["trans_date_trans_time"], 
        errors="coerce"
    )

    # If we want to ensure we have some valid timestamps, fill NaT => drop or fill
    # We'll just fill them with a default so we don't drop everything
    df["trans_date_trans_time"] = df["trans_date_trans_time"].fillna(method="ffill")

    # 3) Extract hour & day_of_week
    df["hour"] = df["trans_date_trans_time"].dt.hour
    df["day_of_week"] = df["trans_date_trans_time"].dt.dayofweek

    # 4) Compute distance: fill missing lat/long with 0.0
    for c in ["lat", "long", "merch_lat", "merch_long"]:
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0.0)

    # naive Euclidean distance in lat/long degrees
    df["distance"] = np.sqrt(
        (df["lat"] - df["merch_lat"])**2 + 
        (df["long"] - df["merch_long"])**2
    )

    # Make sure is_fraud is int
    df["is_fraud"] = df["is_fraud"].astype(int)

    # 5) Keep columns that actually exist & won't yield empty data
    # We'll skip 'dob' to avoid missing data issues
    keep_cols = [
        "amt",         # transaction amount
        "category",
        "gender",
        "state",
        "city_pop",
        "hour",
        "day_of_week",
        "distance",
        "is_fraud"     # target
    ]
    df = df[keep_cols]
    # If any row is missing in these columns, we can fill or drop. We'll fill numeric with 0
    df["city_pop"] = pd.to_numeric(df["city_pop"], errors="coerce").fillna(0.0)
    df["gender"] = df["gender"].fillna("U")   # unknown
    df["state"]  = df["state"].fillna("XX")   # unknown
    df["category"] = df["category"].fillna("other")

    # That's it. We keep all rows. 
    print("Final shape after feature engineering:", df.shape)
    return df


def build_pipeline():
    """
    Creates a pipeline:
      - ColumnTransformer for numeric vs. categorical
      - SMOTE for class balance
      - RandomForest
    """
    numeric_feats = ["amt", "city_pop", "hour", "day_of_week", "distance"]
    cat_feats = ["category", "gender", "state"]

    numeric_transformer = StandardScaler()
    cat_transformer = OneHotEncoder(handle_unknown="ignore")

    preprocessor = ColumnTransformer([
        ("num", numeric_transformer, numeric_feats),
        ("cat", cat_transformer, cat_feats)
    ])

    rf = RandomForestClassifier(random_state=42, n_jobs=-1)

    # ImbPipeline from imblearn so SMOTE occurs after transforms
    pipeline = ImbPipeline([
        ("preprocessor", preprocessor),
        ("smote", SMOTE(random_state=42)),
        ("rf", rf)
    ])
    return pipeline


def main():
    # Load data
    df = load_data("app/ml/credit_card_transactions.csv")
    print(df.head())  # debug first 5 rows

    # Separate features & target
    X = df.drop("is_fraud", axis=1)
    y = df["is_fraud"].values

    # Split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )
    print("Train shape:", X_train.shape, "Test shape:", X_test.shape)

    pipeline = build_pipeline()

    # Let's do a small hyperparam search
    param_dist = {
        "rf__n_estimators": [50, 100],
        "rf__max_depth": [5, 10, None],
        "rf__min_samples_split": [2, 5],
        "rf__min_samples_leaf": [1, 2],
    }

    from sklearn.model_selection import RandomizedSearchCV

    search = RandomizedSearchCV(
        pipeline,
        param_dist,
        n_iter=4,        # small for demo
        scoring="f1",
        cv=3,
        verbose=2,
        n_jobs=-1,
        random_state=42
    )

    search.fit(X_train, y_train)
    best_model = search.best_estimator_
    print("Best params:", search.best_params_)

    # Evaluate default threshold=0.5
    y_pred = best_model.predict(X_test)
    print("Classification report @ threshold=0.5:")
    print(classification_report(y_test, y_pred))

    # Probability + threshold tuning
    probs = best_model.predict_proba(X_test)[:, 1]
    thresholds = np.linspace(0, 1, 50)
    best_thr = 0.5
    best_f1 = -1
    for t in thresholds:
        temp_pred = (probs >= t).astype(int)
        f1 = f1_score(y_test, temp_pred)
        if f1 > best_f1:
            best_f1 = f1
            best_thr = t

    print(f"Best threshold by F1: {best_thr:.3f} (F1={best_f1:.3f})")
    final_preds = (probs >= best_thr).astype(int)
    print("Classification report @ best threshold:")
    print(classification_report(y_test, final_preds))

    # Save model
    model_data = {
        "model": best_model,
        "threshold": best_thr
    }
    joblib.dump(model_data, "app/ml/rf_model.pkl")
    print("Saved rf_model.pkl with best threshold.")


if __name__ == "__main__":
    main()
