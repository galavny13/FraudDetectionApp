# parse_statement.py

import pdfplumber
import pandas as pd
import cv2
import pytesseract
import numpy as np
import re
import os
from PIL import Image

# Define patterns / lookups
TRANSACTION_TYPES = {"purchase", "refund", "withdrawal", "payment", "credit", "debit"}
CURRENCY_ALIASES = {
    "usp": "USD",
    "usb": "USD",
    "us0": "USD",
    "usd": "USD",
    # Add more if needed
}

def extract_transactions_from_table_pdf(pdf_path: str) -> pd.DataFrame:
    """
    Extract transactions from a tabular PDF using pdfplumber.
    Expects columns: Date, Merchant, Category, Amount, Currency, Transaction Type
    """
    transactions = []
    try:
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                tables = page.extract_tables()
                for table in tables:
                    # Each table is a list of rows, where each row is a list of string cells
                    for row in table:
                        if len(row) < 6:
                            continue
                        # Skip potential header row
                        if row[0].strip().lower() == "date" or row[3].strip().lower() == "amount":
                            continue
                        try:
                            date_str = row[0].strip()
                            merchant_str = row[1].strip()
                            category_str = row[2].strip()
                            raw_amount = row[3].strip().replace(",", "")
                            amount_val = float(raw_amount)
                            currency_str = row[4].strip()
                            transaction_type_str = row[5].strip()

                            transactions.append({
                                "Date": date_str,
                                "Merchant": merchant_str,
                                "Category": category_str,
                                "Amount": amount_val,
                                "Currency": currency_str,
                                "Type": transaction_type_str
                            })
                        except Exception as e:
                            print(f"[WARN] Skipped row in PDF parse due to error: {e} => {row}")
    except Exception as e:
        print(f"[ERROR] Failed to process PDF at {pdf_path}: {e}")

    return pd.DataFrame(transactions)


def extract_transactions_from_image(image_path: str) -> pd.DataFrame:
    """
    Extract transactions from an image of a statement using OpenCV + Tesseract.
    We use a more flexible approach:
      1) Use morphological ops + threshold to isolate text.
      2) OCR the text line by line.
      3) For each line, attempt to find date, transaction type, currency, and amount.
      4) Whatever remains in the middle is merchant/category.
    """
    transactions = []
    try:
        img = cv2.imread(image_path)
        if img is None:
            print(f"[ERROR] Unable to read image: {image_path}")
            return pd.DataFrame()

        # Convert to grayscale
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Thresholding (inverse)
        # If lighting is inconsistent, consider using adaptive thresholding:
        # table_structure = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        #                                         cv2.THRESH_BINARY_INV, 11, 2)
        _, binary = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY_INV)

        # Detect horizontal lines
        kernel = np.ones((1, 50), np.uint8)
        horizontal_lines = cv2.morphologyEx(binary, cv2.MORPH_OPEN, kernel)

        # Subtract lines => table_structure
        table_structure = cv2.subtract(binary, horizontal_lines)

        # OCR
        extracted_text = pytesseract.image_to_string(table_structure, config="--psm 6")
        rows = extracted_text.strip().split("\n")

        for row in rows:
            row_clean = re.sub(r"[\|,]", " ", row).strip()
            # Normalize common currency OCR mistakes (usp->USD, usb->USD, etc.)
            for bad_cur, good_cur in CURRENCY_ALIASES.items():
                # case-insensitive replace
                row_clean = re.sub(bad_cur, good_cur, row_clean, flags=re.IGNORECASE)

            # Split on whitespace
            tokens = re.split(r"\s+", row_clean)

            # Attempt to parse using a pattern-based approach
            parsed = parse_ocr_line(tokens)
            if parsed is not None:
                transactions.append(parsed)
            # else we skip the row (and might see a [WARN] in parse_ocr_line)
    except Exception as ex:
        print(f"[ERROR] Failed to process image {image_path}: {ex}")

    return pd.DataFrame(transactions)


def parse_ocr_line(tokens):
    """
    Given a list of tokens from one OCR'd line, attempt to extract:
      - Date (YYYY-MM-DD) near the start
      - Transaction Type (purchase/refund/withdrawal, etc.) near the end
      - Currency (USD, etc.) near the end
      - Amount (float) near the currency
      - Everything else becomes Merchant/Category
    If we can't parse correctly, return None.
    """

    # Filter out obviously spurious tokens like '-' or '|' if they remain
    tokens = [t for t in tokens if t not in ("-", "|")]

    if len(tokens) < 5:
        return None

    # 1) Identify date near the front (we look for a pattern like YYYY-MM-DD)
    date_str = None
    if re.match(r"^\d{4}-\d{2}-\d{2}$", tokens[0]):
        date_str = tokens[0]
        idx_start_merchant = 1
    else:
        # If the first token isn't a date, skip (or you can try searching further)
        return None

    # 2) Identify transaction type near the end
    # We'll search from the right for a known transaction type
    tx_type_idx = -1
    transaction_type_str = None
    for i in range(len(tokens)-1, -1, -1):
        maybe_type = re.sub(r"[^\w]", "", tokens[i].lower())  # remove punctuation, make lower
        if maybe_type in TRANSACTION_TYPES:
            transaction_type_str = tokens[i]
            tx_type_idx = i
            break
    if not transaction_type_str:
        # No recognized transaction type => skip
        return None

    # 3) Identify currency near the type (e.g., the token to the left might be "USD")
    currency_idx = tx_type_idx - 1
    if currency_idx < 1:
        return None
    currency_str = tokens[currency_idx].upper()

    # If for some reason it's not recognized, you could skip or assume "USD"
    # We'll just accept anything as a currency token if it matches "USD" or similar.
    if currency_str not in ("USD",):
        # If you want to accept "usd" or other currency codes, add them here:
        # or do a more flexible check => if re.match(r"^[A-Za-z]{3}$", currency_str)
        return None

    # 4) Identify amount near the currency (one token to the left)
    amount_idx = currency_idx - 1
    if amount_idx < 1:
        return None
    amount_str = tokens[amount_idx].replace(",", "")
    try:
        amount_val = float(amount_str)
    except ValueError:
        return None

    # 5) Next token to the left is presumably the category (optional).
    # This is a guess. You could skip if you want to treat everything in the middle as merchant & category combined.
    category_idx = amount_idx - 1

    # If we run out of tokens, we skip
    if category_idx < idx_start_merchant:
        # We have no category => let's assume we skip it or treat it as "misc"
        category_str = "misc"
        idx_end_merchant = amount_idx  # merchant from [1 .. amount_idx-1]
    else:
        category_str = tokens[category_idx]
        idx_end_merchant = category_idx

    # 6) Merchant tokens are in between the date and the category
    merchant_tokens = tokens[idx_start_merchant:idx_end_merchant]
    merchant_str = " ".join(merchant_tokens)

    # Build a dict with the extracted info
    parsed_line = {
        "Date": date_str,
        "Merchant": merchant_str,
        "Category": category_str,
        "Amount": amount_val,
        "Currency": currency_str,
        "Type": transaction_type_str
    }

    return parsed_line


def parse_statement(file_path: str) -> pd.DataFrame:
    """
    1) Decide if file is PDF or Image based on extension.
    2) Parse transactions into a DataFrame with columns:
       Date, Merchant, Category, Amount, Currency, Type
    3) Rename columns to match the training set:
       trans_date_trans_time, merchant, category, amt, currency, transaction_type
    4) Add placeholder columns for hour, day_of_week, city_pop, distance, gender, state
       so that we can pass them into the same pipeline that was trained on CSV data.
    """
    ext = os.path.splitext(file_path)[1].lower()
    if ext == ".pdf":
        df = extract_transactions_from_table_pdf(file_path)
    else:
        df = extract_transactions_from_image(file_path)

    if df.empty:
        return df  # no rows => return empty DataFrame

    # Rename columns to align with training
    rename_map = {
        "Date": "trans_date_trans_time",
        "Merchant": "merchant",
        "Category": "category",
        "Amount": "amt",
        "Type": "transaction_type",
        "Currency": "currency",
    }
    df = df.rename(columns=rename_map)

    # Convert date
    if "trans_date_trans_time" in df.columns:
        df["trans_date_trans_time"] = pd.to_datetime(df["trans_date_trans_time"], errors="coerce")
    else:
        df["trans_date_trans_time"] = pd.NaT

    # Create placeholders for columns your model or comparison code might expect
    if "hour" not in df.columns:
        df["hour"] = df["trans_date_trans_time"].dt.hour.fillna(0).astype(int)
    if "day_of_week" not in df.columns:
        df["day_of_week"] = df["trans_date_trans_time"].dt.dayofweek.fillna(0).astype(int)
    if "city_pop" not in df.columns:
        df["city_pop"] = 1000.0
    if "distance" not in df.columns:
        df["distance"] = 0.5
    if "gender" not in df.columns:
        df["gender"] = "U"
    if "state" not in df.columns:
        df["state"] = "XX"

    return df
