from sqlalchemy.orm import Session
from database.models import Customer, CreditProduct, CreditAgreement, CreditTransaction, TransactionType
from typing import List, Dict, Any


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
    return query.all()


def get_credit_products(session: Session) -> List[CreditProduct]:
    """
    Получение всех кредитных продуктов.
    :param session: Сессия базы данных.
    :return: Список объектов CreditProduct.
    """
    return session.query(CreditProduct).all()


def get_transactions_by_customer(
    session: Session,
    customer_id: int
) -> List[CreditTransaction]:
    """
    Получение транзакций по ID клиента.
    :param session: Сессия базы данных.
    :param customer_id: ID клиента.
    :return: Список объектов CreditTransaction.
    """
    return session.query(CreditTransaction).filter(
        CreditTransaction.CustomerID == customer_id
    ).all()


def get_credit_agreements_by_customer(
    session: Session,
    customer_id: int
) -> List[CreditAgreement]:
    """
    Получение кредитных договоров клиента.
    :param session: Сессия базы данных.
    :param customer_id: ID клиента.
    :return: Список объектов CreditAgreement.
    """
    return session.query(CreditAgreement).filter(
        CreditAgreement.CustomerID == customer_id
    ).all()
