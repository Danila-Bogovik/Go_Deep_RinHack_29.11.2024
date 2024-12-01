import pandas as pd
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from database.models import Customer, CreditProduct, CreditAgreement, TransactionType, CreditTransaction
from datetime import datetime


def load_csv_to_db(
        session: Session,
        model,
        csv_file: str,
        replace: bool = False,
        validate: bool = True
):
    """
    Загрузка данных из CSV в базу данных.
    :param session: Сессия базы данных.
    :param model: Модель SQLAlchemy.
    :param csv_file: Путь к файлу CSV.
    :param replace: Заменить данные (True) или добавить (False).
    :param validate: Проверять данные перед загрузкой (True) или нет.
    """
    try:
        data = pd.read_csv(csv_file)

        # Если нужно, очищаем таблицу перед загрузкой
        if replace:
            session.query(model).delete()
            session.commit()

        # Валидация данных перед загрузкой
        if validate:
            data = validate_data(data, model)

        # Загрузка данных в базу
        session.bulk_insert_mappings(model, data.to_dict(orient="records"))
        session.commit()
        print(f"Данные из {csv_file} успешно загружены в таблицу {model.__tablename__}.")

    except IntegrityError as e:
        session.rollback()
        print(f"Ошибка целостности данных при загрузке {csv_file}: {e}")

    except Exception as e:
        session.rollback()
        print(f"Произошла ошибка при загрузке {csv_file}: {e}")


def validate_data(data: pd.DataFrame, model):
    """
    Валидирует данные перед загрузкой.
    :param data: DataFrame с данными.
    :param model: Модель SQLAlchemy.
    :return: DataFrame с валидными данными.
    """
    # Пример простой проверки: удаление дубликатов
    data = data.drop_duplicates()

    # Дополнительная проверка для каждой модели
    if model == Customer:
        required_columns = ["CustomerTypeID", "Name", "TIN"]
    elif model == CreditProduct:
        required_columns = ["ProductName", "InterestRate", "MaxLoanAmount", "MinRepaymentTerm"]
    elif model == CreditAgreement:
        required_columns = ["CustomerID", "CreditProductID", "AgreementDate", "LoanAmount"]
    elif model == TransactionType:
        required_columns = ["TransactionTypeName"]
    elif model == CreditTransaction:
        required_columns = ["CustomerID", "CreditAgreementID", "TransactionDate", "TransactionAmount"]

    # Проверяем наличие обязательных колонок
    for column in required_columns:
        if column not in data.columns:
            raise ValueError(f"Отсутствует обязательная колонка '{column}' для модели {model.__name__}.")

    return data


def export_table_to_csv(session: Session, model, csv_file: str):
    """
    Экспортирует данные из таблицы в CSV.
    :param session: Сессия базы данных.
    :param model: Модель SQLAlchemy.
    :param csv_file: Путь к файлу CSV для сохранения.
    """
    try:
        # Получаем данные из таблицы
        data = session.query(model).all()

        # Преобразуем данные в DataFrame
        df = pd.DataFrame([row.__dict__ for row in data])
        df = df.drop("_sa_instance_state", axis=1, errors="ignore")  # Убираем системное поле

        # Сохраняем в CSV
        df.to_csv(csv_file, index=False)
        print(f"Данные из таблицы {model.__tablename__} успешно экспортированы в файл {csv_file}.")
    except Exception as e:
        print(f"Произошла ошибка при экспорте данных из {model.__tablename__}: {e}")


def backup_database(session: Session, backup_dir: str):
    """
    Создает резервную копию всех таблиц базы данных в формате CSV.
    :param session: Сессия базы данных.
    :param backup_dir: Директория для сохранения файлов.
    """
    from pathlib import Path

    Path(backup_dir).mkdir(parents=True, exist_ok=True)

    for model in [Customer, CreditProduct, CreditAgreement, TransactionType, CreditTransaction]:
        csv_file = f"{backup_dir}/{model.__tablename__}.csv"
        export_table_to_csv(session, model, csv_file)


def update_data_from_csv(session: Session, model, csv_file: str):
    """
    Обновляет данные в таблице из CSV.
    :param session: Сессия базы данных.
    :param model: Модель SQLAlchemy.
    :param csv_file: Путь к файлу CSV.
    """
    try:
        data = pd.read_csv(csv_file)
        for index, row in data.iterrows():
            # Ищем запись по первичному ключу
            primary_key = list(model.__table__.primary_key.columns.keys())[0]
            record = session.query(model).get(row[primary_key])

            if record:
                # Обновляем поля
                for key, value in row.items():
                    if hasattr(record, key):
                        setattr(record, key, value)
            else:
                # Добавляем новую запись, если не найдено
                session.add(model(**row.to_dict()))

        session.commit()
        print(f"Данные из {csv_file} успешно обновлены в таблице {model.__tablename__}.")
    except Exception as e:
        session.rollback()
        print(f"Произошла ошибка при обновлении данных из {csv_file}: {e}")


def delete_data_from_csv(session: Session, model, csv_file: str):
    """
    Удаляет данные из таблицы, перечисленные в CSV.
    :param session: Сессия базы данных.
    :param model: Модель SQLAlchemy.
    :param csv_file: Путь к файлу CSV.
    """
    try:
        data = pd.read_csv(csv_file)
        primary_key = list(model.__table__.primary_key.columns.keys())[0]

        for value in data[primary_key]:
            record = session.query(model).get(value)
            if record:
                session.delete(record)

        session.commit()
        print(f"Данные из {csv_file} успешно удалены из таблицы {model.__tablename__}.")
    except Exception as e:
        session.rollback()
        print(f"Произошла ошибка при удалении данных из {csv_file}: {e}")
