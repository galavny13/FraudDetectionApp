# backend/app/models.py
from sqlalchemy import Column, Integer, String, Boolean, Float, Text
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(String, nullable=True)
    merchant_name = Column(String, nullable=True)
    merchant_category = Column(String, nullable=True)
    transaction_amount = Column(Float, nullable=True)
    currency = Column(String, nullable=True)
    transaction_type = Column(String, nullable=True)
    remaining_credit_limit = Column(Float, nullable=True)

    fraud_detected = Column(Boolean, default=False)
    explanation = Column(Text, nullable=True)
    probability = Column(Float, nullable=True)
