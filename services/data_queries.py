from sqlalchemy.orm import Session
from sqlalchemy.sql import func
from database.models import (
    Customer, CreditProduct, CreditAgreement,
    CreditTransaction, TransactionType
)
from typing import List, Dict, Any, Optional


def get_customers(session: Session, filters: Dict[str, Any] = None) -> List[Customer]:
    """
    Получение списка клиентов с возможностью фильтрации.
    :param session: Сессия базы данных.
    :param filters: Словарь с фильтрами.
    :return: Список объектов Customer.
    """
    query = session.query(Customer)
    if filters:
        if "CustomerTypeID" in filters:
            query = query.filter(Customer.CustomerTypeID == filters["CustomerTypeID"])
        if "Name" in filters:
            query = query.filter(Customer.Name.like(f"%{filters['Name']}%"))
        if "TIN" in filters:
            query = query.filter(Customer.TIN == filters["TIN"])
    return query.all()


def get_credit_products(session: Session, filters: Dict[str, Any] = None) -> List[CreditProduct]:
    """
    Получение всех кредитных продуктов с возможностью фильтрации.
    :param session: Сессия базы данных.
    :param filters: Словарь с фильтрами.
    :return: Список объектов CreditProduct.
    """
    query = session.query(CreditProduct)
    if filters:
        if "MaxLoanAmount" in filters:
            query = query.filter(CreditProduct.MaxLoanAmount >= filters["MaxLoanAmount"])
        if "InterestRate" in filters:
            query = query.filter(CreditProduct.InterestRate <= filters["InterestRate"])
        if "CollateralRequired" in filters:
            query = query.filter(CreditProduct.CollateralRequired == filters["CollateralRequired"])
    return query.all()


def get_transactions_by_customer(
    session: Session,
    customer_id: int,
    transaction_type: Optional[int] = None,
    date_range: Optional[Dict[str, str]] = None
) -> List[CreditTransaction]:
    """
    Получение транзакций по ID клиента с возможностью фильтрации по типу и дате.
    :param session: Сессия базы данных.
    :param customer_id: ID клиента.
    :param transaction_type: ID типа транзакции.
    :param date_range: Словарь с ключами "start" и "end" для диапазона дат.
    :return: Список объектов CreditTransaction.
    """
    query = session.query(CreditTransaction).filter(
        CreditTransaction.CustomerID == customer_id
    )
    if transaction_type:
        query = query.filter(CreditTransaction.TransactionTypeID == transaction_type)
    if date_range:
        if "start" in date_range:
            query = query.filter(CreditTransaction.TransactionDate >= date_range["start"])
        if "end" in date_range:
            query = query.filter(CreditTransaction.TransactionDate <= date_range["end"])
    return query.all()


def get_credit_agreements_by_customer(
    session: Session,
    customer_id: int,
    active_only: bool = False
) -> List[CreditAgreement]:
    """
    Получение кредитных договоров клиента с возможностью фильтрации только активных.
    :param session: Сессия базы данных.
    :param customer_id: ID клиента.
    :param active_only: Возвращать только активные договоры.
    :return: Список объектов CreditAgreement.
    """
    query = session.query(CreditAgreement).filter(
        CreditAgreement.CustomerID == customer_id
    )
    if active_only:
        query = query.filter(CreditAgreement.IsActive == True)
    return query.all()


def get_aggregated_transaction_summary(
    session: Session,
    customer_id: Optional[int] = None
) -> Dict[str, Any]:
    """
    Получение агрегированных данных по транзакциям (сумма, среднее, количество).
    :param session: Сессия базы данных.
    :param customer_id: ID клиента (опционально).
    :return: Словарь с агрегированными данными.
    """
    query = session.query(
        func.sum(CreditTransaction.TransactionAmount).label("total_amount"),
        func.avg(CreditTransaction.TransactionAmount).label("average_amount"),
        func.count(CreditTransaction.TransactionID).label("transaction_count")
    )
    if customer_id:
        query = query.filter(CreditTransaction.CustomerID == customer_id)
    result = query.one()
    return {
        "total_amount": result.total_amount,
        "average_amount": result.average_amount,
        "transaction_count": result.transaction_count
    }


def get_top_customers_by_loans(
    session: Session,
    limit: int = 10
) -> List[Dict[str, Any]]:
    """
    Получение топ клиентов по сумме кредитов.
    :param session: Сессия базы данных.
    :param limit: Максимальное количество клиентов в результате.
    :return: Список словарей с данными о клиентах.
    """
    query = session.query(
        Customer.Name,
        func.sum(CreditAgreement.LoanAmount).label("total_loans")
    ).join(CreditAgreement, CreditAgreement.CustomerID == Customer.CustomerID) \
        .group_by(Customer.CustomerID) \
        .order_by(func.sum(CreditAgreement.LoanAmount).desc()) \
        .limit(limit)

    return [{"Name": row.Name, "TotalLoans": row.total_loans} for row in query.all()]


def get_transaction_types(session: Session) -> List[TransactionType]:
    """
    Получение всех типов транзакций.
    :param session: Сессия базы данных.
    :return: Список объектов TransactionType.
    """
    return session.query(TransactionType).all()


def get_credit_products_with_active_agreements(session: Session) -> List[Dict[str, Any]]:
    """
    Получение кредитных продуктов с количеством активных соглашений.
    :param session: Сессия базы данных.
    :return: Список словарей с данными о продуктах.
    """
    query = session.query(
        CreditProduct.ProductName,
        func.count(CreditAgreement.CreditAgreementID).label("active_agreements")
    ).join(CreditAgreement, CreditAgreement.CreditProductID == CreditProduct.CreditProductID) \
        .filter(CreditAgreement.IsActive == True) \
        .group_by(CreditProduct.ProductName)

    return [{"ProductName": row.ProductName, "ActiveAgreements": row.active_agreements} for row in query.all()]
