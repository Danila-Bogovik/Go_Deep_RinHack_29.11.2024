from sqlalchemy import (
    Column, Integer, String, Float, Date, Boolean, ForeignKey, Text
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()

# Клиенты
class Customer(Base):
    __tablename__ = "customers"

    CustomerID = Column(Integer, primary_key=True)
    CustomerTypeID = Column(Integer, nullable=False)
    Name = Column(String, nullable=False)
    DateOfBirth = Column(Date, nullable=True)
    RegistrationDate = Column(Date, nullable=True)
    TIN = Column(String, nullable=False, unique=True)  # Taxpayer Identification Number
    ContactInfo = Column(String, nullable=True)

    agreements = relationship("CreditAgreement", back_populates="customer")
    transactions = relationship("CreditTransaction", back_populates="customer")
    complaints = relationship("CustomerComplaint", back_populates="customer")  # Новое

# Кредитные продукты
class CreditProduct(Base):
    __tablename__ = "credit_products"

    CreditProductID = Column(Integer, primary_key=True)
    ProductName = Column(String, nullable=False)
    InterestRate = Column(Float, nullable=False)
    MaxLoanAmount = Column(Float, nullable=False)
    MinRepaymentTerm = Column(Integer, nullable=False)
    CollateralRequired = Column(Boolean, nullable=False)
    Description = Column(Text, nullable=True)  # Новое поле

    agreements = relationship("CreditAgreement", back_populates="credit_product")
    product_ratings = relationship("ProductRating", back_populates="credit_product")  # Новое

# Кредитные соглашения
class CreditAgreement(Base):
    __tablename__ = "credit_agreements"

    CreditAgreementID = Column(Integer, primary_key=True)
    CustomerID = Column(Integer, ForeignKey("customers.CustomerID"), nullable=False)
    CreditProductID = Column(Integer, ForeignKey("credit_products.CreditProductID"), nullable=False)
    AgreementDate = Column(Date, nullable=False)
    LoanAmount = Column(Float, nullable=False)
    LoanTerm = Column(Integer, nullable=False)
    InterestRate = Column(Float, nullable=False)
    IsActive = Column(Boolean, default=True)  # Новое поле: Активно ли соглашение

    customer = relationship("Customer", back_populates="agreements")
    credit_product = relationship("CreditProduct", back_populates="agreements")
    transactions = relationship("CreditTransaction", back_populates="agreement")

# Типы транзакций
class TransactionType(Base):
    __tablename__ = "transaction_types"

    TransactionTypeID = Column(Integer, primary_key=True)
    TransactionTypeName = Column(String, nullable=False)

    transactions = relationship("CreditTransaction", back_populates="transaction_type")

# Кредитные транзакции
class CreditTransaction(Base):
    __tablename__ = "credit_transactions"

    TransactionID = Column(Integer, primary_key=True)
    CustomerID = Column(Integer, ForeignKey("customers.CustomerID"), nullable=False)
    CreditAgreementID = Column(Integer, ForeignKey("credit_agreements.CreditAgreementID"), nullable=False)
    TransactionDate = Column(Date, nullable=False)
    TransactionAmount = Column(Float, nullable=False)
    TransactionTypeID = Column(Integer, ForeignKey("transaction_types.TransactionTypeID"), nullable=False)
    Notes = Column(Text, nullable=True)  # Новое поле: заметки к транзакции

    customer = relationship("Customer", back_populates="transactions")
    agreement = relationship("CreditAgreement", back_populates="transactions")
    transaction_type = relationship("TransactionType", back_populates="transactions")

# Жалобы клиентов
class CustomerComplaint(Base):
    __tablename__ = "customer_complaints"

    ComplaintID = Column(Integer, primary_key=True)
    CustomerID = Column(Integer, ForeignKey("customers.CustomerID"), nullable=False)
    ComplaintDate = Column(Date, nullable=False)
    ComplaintText = Column(Text, nullable=False)
    Status = Column(String, default="Open")  # Статус жалобы: Open, In Progress, Closed

    customer = relationship("Customer", back_populates="complaints")

# Рейтинги кредитных продуктов
class ProductRating(Base):
    __tablename__ = "product_ratings"

    RatingID = Column(Integer, primary_key=True)
    CreditProductID = Column(Integer, ForeignKey("credit_products.CreditProductID"), nullable=False)
    CustomerID = Column(Integer, ForeignKey("customers.CustomerID"), nullable=False)
    Rating = Column(Integer, nullable=False)  # Оценка от 1 до 5
    ReviewText = Column(Text, nullable=True)  # Отзыв

    credit_product = relationship("CreditProduct", back_populates="product_ratings")
    customer = relationship("Customer")  # Односторонняя связь

# Методы для удобной работы с новыми данными
def add_complaint(session, customer_id: int, complaint_text: str):
    """
    Добавляет жалобу клиента.
    """
    complaint = CustomerComplaint(
        CustomerID=customer_id,
        ComplaintDate=datetime.utcnow(),
        ComplaintText=complaint_text
    )
    session.add(complaint)
    session.commit()
    return complaint

def resolve_complaint(session, complaint_id: int):
    """
    Закрывает жалобу клиента.
    """
    complaint = session.query(CustomerComplaint).filter_by(ComplaintID=complaint_id).first()
    if not complaint:
        raise ValueError("Жалоба не найдена")

    complaint.Status = "Closed"
    session.commit()

def rate_product(session, customer_id: int, credit_product_id: int, rating: int, review_text: str = None):
    """
    Добавляет или обновляет рейтинг кредитного продукта.
    """
    if not (1 <= rating <= 5):
        raise ValueError("Рейтинг должен быть от 1 до 5")

    product_rating = session.query(ProductRating).filter_by(
        CustomerID=customer_id,
        CreditProductID=credit_product_id
    ).first()

    if product_rating:
        product_rating.Rating = rating
        product_rating.ReviewText = review_text
    else:
        product_rating = ProductRating(
            CreditProductID=credit_product_id,
            CustomerID=customer_id,
            Rating=rating,
            ReviewText=review_text
        )
        session.add(product_rating)

    session.commit()
    return product_rating
