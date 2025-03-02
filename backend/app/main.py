# main.py

import os
import uuid
import shutil

from fastapi import FastAPI, File, UploadFile, Form, Depends
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

import joblib
import pandas as pd

from app.database import engine, get_db
from app.models import Base, Transaction
from app.parse_statement import parse_statement
from app.send_email import send_fraud_alert

# Create all tables if needed
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Fraud Detection API", version="1.0.0")

# CORS MIDDLEWARE (adjust allowed_origins as needed)
allowed_origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# LOAD MODEL
model_data = joblib.load("app/ml/rf_model.pkl")
rf_model = model_data["model"]
threshold = model_data["threshold"]

@app.post("/analyze-statement")
async def analyze_statement(
    file: UploadFile = File(...),
    contact_email: str = Form(None),
    db: Session = Depends(get_db),
):
    """
    1. Receive an uploaded PDF/Image of a credit card statement.
    2. Parse statement => DataFrame.
    3. For each row => run model => store => if fraud => notify.
    """
    # 1) Save to a temp file
    ext = os.path.splitext(file.filename)[1].lower()
    temp_filename = f"{uuid.uuid4()}{ext}"
    temp_path = f"/tmp/{temp_filename}"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 2) Parse transactions
    df = parse_statement(temp_path)

    # If no rows found, return early
    if df.empty:
        return JSONResponse(
            {
                "error": "No transactions found or parse error.",
                "fileName": file.filename,
            },
            status_code=400,
        )

    # 3) Convert any boolean or numpy dtypes if needed
    for col in df.columns:
        if pd.api.types.is_bool_dtype(df[col]):
            df[col] = df[col].astype(bool)

    # 4) Evaluate each row => model => DB => detect fraud
    output_rows = []
    any_fraud_detected = False
    fraud_details = []

    for idx, row in df.iterrows():
        date_str = str(row.get("trans_date_trans_time", ""))
        merchant_str = str(row.get("merchant", ""))
        category_str = str(row.get("category", ""))
        # handle amount
        try:
            amount_val = float(row.get("amt", 0.0))
        except ValueError:
            amount_val = 0.0
        currency_str = str(row.get("currency", ""))
        transaction_type = str(row.get("transaction_type", ""))

        # Build a single-row DF with the columns your model expects
        # In your training pipeline, you used: ["amt","category","gender","state","city_pop","hour","day_of_week","distance"]
        X_sample = pd.DataFrame([{
            "amt": amount_val,
            "category": category_str.lower().replace(" ", "_"),
            "gender": row.get("gender", "U"),
            "state": row.get("state", "XX"),
            "city_pop": row.get("city_pop", 1000.0),
            "hour": row.get("hour", 0),
            "day_of_week": row.get("day_of_week", 0),
            "distance": row.get("distance", 0.5),
        }])

        # Predict probability
        prob = rf_model.predict_proba(X_sample)[0, 1]
        is_fraud = (prob >= threshold)
        explanation = (
            f"Fraud probability={prob:.2f} >= threshold={threshold:.2f}"
            if is_fraud
            else f"No fraud (prob={prob:.2f} < threshold={threshold:.2f})"
        )

        if is_fraud:
            any_fraud_detected = True
            fraud_details.append(
                f"Merchant={merchant_str}, Amount={amount_val}, Prob={prob:.2f}"
            )

        # Save to DB
        tx = Transaction(
            date=date_str,
            merchant_name=merchant_str,
            merchant_category=category_str,
            transaction_amount=amount_val,
            currency=currency_str,
            transaction_type=transaction_type,
            remaining_credit_limit=9999.0,  # placeholder
            fraud_detected=is_fraud,
            explanation=explanation,
            probability=prob,
        )
        db.add(tx)
        db.commit()
        db.refresh(tx)

        output_rows.append({
            "date": date_str,
            "merchant": merchant_str,
            "category": category_str,
            "amount": amount_val,
            "currency": currency_str,
            "type": transaction_type,
            "fraud_detected": bool(is_fraud),
            "explanation": explanation,
            "probability": prob,
        })

    # 5) Send email if fraud
    if any_fraud_detected and contact_email:
        detail_msg = "\n".join(fraud_details)
        send_fraud_alert(contact_email, detail_msg)

    # 6) Return JSON
    return JSONResponse(
        content=jsonable_encoder({
            "status": "ok",
            "fileName": file.filename,
            "rows": output_rows,
        })
    )


@app.get("/health")
def health():
    return {"status": "running", "version": "1.0.0"}
