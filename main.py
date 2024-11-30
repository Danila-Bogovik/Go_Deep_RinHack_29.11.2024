from database.db_operations import get_engine, create_database, get_session
from database.models import Customer, CreditProduct, CreditAgreement, TransactionType, CreditTransaction
from services.csv_loader import load_csv_to_db

def main():
    engine = get_engine()
    create_database(engine)
    session = get_session(engine)

    # Пример загрузки данных
    load_csv_to_db(session, Customer, "customers.csv", replace=True)
    load_csv_to_db(session, CreditProduct, "credit_products.csv", replace=False)

    # Пример фильтрации
    customers = session.query(Customer).filter(Customer.CustomerTypeID == 1).all()
    for customer in customers:
        print(customer.Name)

if __name__ == "__main__":
    main()
