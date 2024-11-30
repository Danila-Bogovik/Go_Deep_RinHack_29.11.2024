# Go_Deep_RinHack_29.11.2024

Проект команды Go Deep по созданию корпоративного хранилища банка от компании Axenix
 
Структура модуля базы данных (без учета веб модуля)

project/
│
├── main.py             # Точка входа
├── database/
│   ├── __init__.py     # Инициализация базы данных
│   ├── models.py       # Определение ORM-моделей
│   ├── db_operations.py# CRUD операции
│
├── services/
│   ├── csv_loader.py   # Загрузка данных из CSV
│   ├── data_queries.py # Запросы данных
│
└── utils/
    ├── config.py       # Настройки приложения



### Описание датасета для хакатона

Данный датасет предназначен для моделирования работы корпоративного хранилища данных банка, фокусируясь на управлении данными о кредитных операциях физических и юридических лиц. Включает информацию о клиентах, кредитных продуктах, договорах, транзакциях и типах операций.

#### **Описание модели данных**
Модель данных состоит из пяти связанных таблиц: 
1. **Customers** — клиенты банка (физические и юридические лица).
2. **CreditProducts** — типы кредитных продуктов, предлагаемых банком.
3. **CreditAgreements** — кредитные договоры, заключённые с клиентами.
4. **TransactionTypes** — типы операций, совершаемых в рамках кредитных договоров.
5. **CreditTransactions** — записи о транзакциях, связанных с кредитами.

Связи между таблицами:
- **Customers** связана с **CreditAgreements** по полю `CustomerID`.
- **CreditProducts** связана с **CreditAgreements** по полю `CreditProductID`.
- **CreditAgreements** связана с **CreditTransactions** по полю `CreditAgreementID`.
- **TransactionTypes** связана с **CreditTransactions** по полю `TransactionTypeID`.

#### **Описание таблиц и полей**

1. **Customers** (Клиенты)
   - **CustomerID** (PK) — уникальный идентификатор клиента.
   - **CustomerTypeID** — тип клиента (1 — физическое лицо, 2 — юридическое лицо).
   - **Name** — имя физического лица или название компании.
   - **DateOfBirth** — дата рождения для физических лиц (null для юридических).
   - **RegistrationDate** — дата регистрации для юридических лиц (null для физических).
   - **TIN** — ИНН клиента (физического или юридического).
   - **ContactInfo** — контактная информация (телефон).

2. **CreditProducts** (Кредитные продукты)
   - **CreditProductID** (PK) — уникальный идентификатор продукта.
   - **ProductName** — название продукта.
   - **InterestRate** — процентная ставка по продукту.
   - **MaxLoanAmount** — максимальная сумма кредита по продукту.
   - **MinRepaymentTerm** — минимальный срок погашения (в месяцах).
   - **CollateralRequired** — требование обеспечения (Да/Нет).

3. **CreditAgreements** (Кредитные договоры)
   - **CreditAgreementID** (PK) — уникальный идентификатор договора.
   - **CustomerID** (FK) — идентификатор клиента, заключившего договор.
   - **CreditProductID** (FK) — идентификатор продукта, связанного с договором.
   - **AgreementDate** — дата заключения договора.
   - **LoanAmount** — сумма кредита.
   - **LoanTerm** — срок кредита (в месяцах).
   - **InterestRate** — процентная ставка договора.

4. **TransactionTypes** (Типы операций)
   - **TransactionTypeID** (PK) — уникальный идентификатор типа операции.
   - **TransactionTypeName** — название типа операции (напр., "Выдача кредита", "Погашение кредита").

5. **CreditTransactions** (Транзакции)
   - **TransactionID** (PK) — уникальный идентификатор транзакции.
   - **CustomerID** (FK) — идентификатор клиента, связанного с транзакцией.
   - **CreditAgreementID** (FK) — идентификатор договора, к которому относится транзакция.
   - **TransactionDate** — дата выполнения операции.
   - **TransactionAmount** — сумма операции.
   - **TransactionTypeID** (FK) — идентификатор типа операции.