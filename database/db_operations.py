from sqlalchemy import create_engine, Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

# Создаем базовый класс для моделей
Base = declarative_base()


# Модели базы данных
class Customer(Base):
    """
    Модель клиента.
    """
    __tablename__ = 'customers'
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    email = Column(String, unique=True, nullable=False)
    phone = Column(String, unique=True, nullable=False)
    accounts = relationship("Account", back_populates="customer")


class Account(Base):
    """
    Модель банковского счета.
    """
    __tablename__ = 'accounts'
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey('customers.id'), nullable=False)
    balance = Column(Float, default=0.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    customer = relationship("Customer", back_populates="accounts")
    transactions = relationship("Transaction", back_populates="account")


class Transaction(Base):
    """
    Модель транзакции.
    """
    __tablename__ = 'transactions'
    id = Column(Integer, primary_key=True)
    account_id = Column(Integer, ForeignKey('accounts.id'), nullable=False)
    amount = Column(Float, nullable=False)
    type = Column(String, nullable=False)  # 'deposit', 'withdraw', 'transfer'
    timestamp = Column(DateTime, default=datetime.utcnow)
    account = relationship("Account", back_populates="transactions")


# Методы для работы с базой данных
def add_customer(session, name: str, email: str, phone: str):
    """
    Добавляет нового клиента.
    """
    customer = Customer(name=name, email=email, phone=phone)
    session.add(customer)
    session.commit()
    return customer


def get_customer_by_id(session, customer_id: int):
    """
    Получает клиента по его ID.
    """
    return session.query(Customer).filter_by(id=customer_id).first()


def get_all_customers(session):
    """
    Возвращает список всех клиентов.
    """
    return session.query(Customer).all()


def add_account(session, customer_id: int):
    """
    Создает банковский счет для клиента.
    """
    account = Account(customer_id=customer_id)
    session.add(account)
    session.commit()
    return account


def get_account_by_id(session, account_id: int):
    """
    Получает счет по его ID.
    """
    return session.query(Account).filter_by(id=account_id).first()


def deposit(session, account_id: int, amount: float):
    """
    Вносит депозит на счет.
    """
    account = get_account_by_id(session, account_id)
    if not account:
        raise ValueError("Счет не найден")

    account.balance += amount
    transaction = Transaction(account_id=account_id, amount=amount, type='deposit')
    session.add(transaction)
    session.commit()
    return account.balance


def withdraw(session, account_id: int, amount: float):
    """
    Снимает средства со счета.
    """
    account = get_account_by_id(session, account_id)
    if not account:
        raise ValueError("Счет не найден")
    if account.balance < amount:
        raise ValueError("Недостаточно средств на счете")

    account.balance -= amount
    transaction = Transaction(account_id=account_id, amount=-amount, type='withdraw')
    session.add(transaction)
    session.commit()
    return account.balance


def transfer(session, from_account_id: int, to_account_id: int, amount: float):
    """
    Переводит средства с одного счета на другой.
    """
    from_account = get_account_by_id(session, from_account_id)
    to_account = get_account_by_id(session, to_account_id)

    if not from_account or not to_account:
        raise ValueError("Один или оба счета не найдены")
    if from_account.balance < amount:
        raise ValueError("Недостаточно средств для перевода")

    from_account.balance -= amount
    to_account.balance += amount

    transaction_out = Transaction(account_id=from_account_id, amount=-amount, type='transfer')
    transaction_in = Transaction(account_id=to_account_id, amount=amount, type='transfer')

    session.add(transaction_out)
    session.add(transaction_in)
    session.commit()
    return from_account.balance, to_account.balance


def get_transactions_by_account(session, account_id: int):
    """
    Возвращает список всех транзакций для указанного счета.
    """
    return session.query(Transaction).filter_by(account_id=account_id).all()


def delete_customer(session, customer_id: int):
    """
    Удаляет клиента и его счета.
    """
    customer = get_customer_by_id(session, customer_id)
    if not customer:
        raise ValueError("Клиент не найден")

    # Удаляем связанные счета и транзакции
    for account in customer.accounts:
        session.query(Transaction).filter_by(account_id=account.id).delete()
        session.delete(account)

    session.delete(customer)
    session.commit()


def delete_account(session, account_id: int):
    """
    Удаляет счет и все его транзакции.
    """
    account = get_account_by_id(session, account_id)
    if not account:
        raise ValueError("Счет не найден")

    session.query(Transaction).filter_by(account_id=account.id).delete()
    session.delete(account)
    session.commit()


def update_customer_info(session, customer_id: int, name: str = None, email: str = None, phone: str = None):
    """
    Обновляет информацию о клиенте.
    """
    customer = get_customer_by_id(session, customer_id)
    if not customer:
        raise ValueError("Клиент не найден")

    if name:
        customer.name = name
    if email:
        customer.email = email
    if phone:
        customer.phone = phone

    session.commit()
    return customer