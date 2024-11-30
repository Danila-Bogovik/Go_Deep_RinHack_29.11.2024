from sqlalchemy import (
    Column, Integer, String, Float, Date, Boolean, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

class Customer(Base):
    __tablename__ = "customers"

    CustomerID = Column(Integer, primary_key=True)
    CustomerTypeID = Column(Integer, nullable=False)
    Name = Column(String, nullable=False)
    DateOfBirth = Column(Date, nullable=True)
    RegistrationDate = Column(Date, nullable=True)
    TIN = Column(String, nullable=False, unique=True)
    ContactInfo = Column(String, nullable=True)

    agreements = relationship("CreditAgreement", back_populates="customer")
    transactions = relationship("CreditTransaction", back_populates="customer")


class CreditProduct(Base):
    __tablename__ = "credit_products"

    CreditProductID = Column(Integer, primary_key=True)
    ProductName = Column(String, nullable=False)
    InterestRate = Column(Float, nullable=False)
    MaxLoanAmount = Column(Float, nullable=False)
    MinRepaymentTerm = Column(Integer, nullable=False)
    CollateralRequired = Column(Boolean, nullable=False)

    agreements = relationship("CreditAgreement", back_populates="credit_product")


class CreditAgreement(Base):
    __tablename__ = "credit_agreements"

    CreditAgreementID = Column(Integer, primary_key=True)
    CustomerID = Column(Integer, ForeignKey("customers.CustomerID"), nullable=False)
    CreditProductID = Column(Integer, ForeignKey("credit_products.CreditProductID"), nullable=False)
    AgreementDate = Column(Date, nullable=False)
    LoanAmount = Column(Float, nullable=False)
    LoanTerm = Column(Integer, nullable=False)
    InterestRate = Column(Float, nullable=False)

    customer = relationship("Customer", back_populates="agreements")
    credit_product = relationship("CreditProduct", back_populates="agreements")
    transactions = relationship("CreditTransaction", back_populates="agreement")


class TransactionType(Base):
    __tablename__ = "transaction_types"

    TransactionTypeID = Column(Integer, primary_key=True)
    TransactionTypeName = Column(String, nullable=False)

    transactions = relationship("CreditTransaction", back_populates="transaction_type")


class CreditTransaction(Base):
    __tablename__ = "credit_transactions"

    TransactionID = Column(Integer, primary_key=True)
    CustomerID = Column(Integer, ForeignKey("customers.CustomerID"), nullable=False)
    CreditAgreementID = Column(Integer, ForeignKey("credit_agreements.CreditAgreementID"), nullable=False)
    TransactionDate = Column(Date, nullable=False)
    TransactionAmount = Column(Float, nullable=False)
    TransactionTypeID = Column(Integer, ForeignKey("transaction_types.TransactionTypeID"), nullable=False)

    customer = relationship("Customer", back_populates="transactions")
    agreement = relationship("CreditAgreement", back_populates="transactions")
    transaction_type = relationship("TransactionType", back_populates="transactions")
