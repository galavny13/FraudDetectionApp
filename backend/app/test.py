import os
import json
import pandas as pd
import joblib

# Import your PDF parser from parse_statement.py
from parse_statement import parse_statement

def main():
    # Load the trained model and threshold
    model_path = os.path.join("ml", "rf_model.pkl")
    try:
        model_data = joblib.load(model_path)
    except Exception as e:
        print(json.dumps({"status": "error", "message": f"Failed to load model: {e}"}, indent=2))
        return

    rf_model = model_data["model"]
    threshold = model_data["threshold"]

    # Parse the PDF statement
    pdf_file = "sample_credit_card_fraud_transactions17.pdf"
    df = parse_statement(pdf_file)
    
    if df.empty:
        print(json.dumps({"status": "error", "message": "No transactions found in the PDF."}, indent=2))
        return

    output_rows = []
    for idx, row in df.iterrows():
        # Prepare features expected by your trained pipeline:
        # Expected features: amt, city_pop, hour, day_of_week, distance, category, gender, state
        try:
            amount_val = float(row.get("amt", 0))
        except Exception:
            amount_val = 0.0

        # Process category (convert to lowercase with underscores)
        category_val = row.get("category", "other")
        category_val = category_val.lower().replace(" ", "_")

        # Create a 1-row DataFrame for prediction with default values for missing features
        feature_dict = {
            "amt": amount_val,
            "city_pop": row.get("city_pop", 1000.0),      # default placeholder
            "hour": row.get("hour", 0),                     # default if not in PDF
            "day_of_week": row.get("day_of_week", 0),       # default if not in PDF
            "distance": row.get("distance", 0.5),           # default placeholder
            "category": category_val,
            "gender": row.get("gender", "U"),               # default placeholder
            "state": row.get("state", "XX")                 # default placeholder
        }
        X_sample = pd.DataFrame([feature_dict])

        # Run the model's prediction
        prob = rf_model.predict_proba(X_sample)[0, 1]
        is_fraud = prob >= threshold
        explanation = (
            f"Fraud probability={prob:.2f} >= threshold={threshold:.2f}"
            if is_fraud else f"No fraud (prob={prob:.2f} < threshold={threshold:.2f})"
        )

        # Format the date string (if the date column was parsed)
        date_val = row.get("trans_date_trans_time")
        if pd.notnull(date_val) and isinstance(date_val, pd.Timestamp):
            date_str = date_val.strftime("%Y-%m-%d %H:%M:%S")
        else:
            date_str = str(date_val)

        # Build the output for this row, converting NumPy types to native Python types
        output_rows.append({
            "date": date_str,
            "merchant": row.get("merchant", ""),
            "category": row.get("category", ""),
            "amount": float(amount_val),
            "currency": row.get("currency", ""),
            "type": row.get("transaction_type", ""),
            "fraud_detected": bool(is_fraud),
            "explanation": explanation,
            "probability": float(prob)
        })

    # Create the JSON response similar to your sample output
    response = {
        "status": "ok",
        "fileName": pdf_file,
        "rows": output_rows
    }
    print(json.dumps(response, indent=2))


if __name__ == "__main__":
    main()
