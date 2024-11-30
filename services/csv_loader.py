import pandas as pd
from sqlalchemy.orm import Session
from database.models import Customer, CreditProduct, CreditAgreement, TransactionType, CreditTransaction

def load_csv_to_db(
    session: Session,
    model,
    csv_file: str,
    replace: bool = False
):
    """
    Загрузка данных из CSV в базу данных.
    :param session: Сессия базы данных.
    :param model: Модель SQLAlchemy.
    :param csv_file: Путь к файлу CSV.
    :param replace: Заменить данные (True) или добавить (False).
    """
    data = pd.read_csv(csv_file)
    if replace:
        session.query(model).delete()
        session.commit()
    session.bulk_insert_mappings(model, data.to_dict(orient="records"))
    session.commit()
