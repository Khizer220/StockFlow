# StockFlow — Inventory & Order Management Platform

**StockFlow** is a backend-focused inventory and order management platform built with Python and FastAPI. It provides REST APIs for managing products, categories, suppliers, customers, inventory, stock movements and customer orders.

The project focuses on backend engineering practices, including layered architecture, database management, JWT authentication, role-based access control, transaction management and automated testing.

**GitHub:** https://github.com/Khizer220/StockFlow

---

## Features

### 1. Authentication & Authorization
- User registration and login.
- JWT-based authentication.
- Secure password hashing using bcrypt.
- Role-based access control (Admin and Staff).
- Protected API endpoints.

### 2. Product Management
- Create, retrieve and update products.
- Unique SKU validation.
- Product descriptions and pricing.
- Product activation and soft deletion.
- Product search, filtering and pagination.

### 3. Category Management
- Create and manage product categories.
- Prevent duplicate category names.
- Update and deactivate categories.

### 4. Supplier Management
- Create and manage suppliers.
- Store supplier contact information.
- Associate suppliers with products.

### 5. Inventory Management
- Track product stock quantities.
- Configure reorder levels.
- Identify low-stock products.
- Update inventory records.

### 6. Stock Movement Management
- Record stock IN and OUT movements.
- Support stock adjustments.
- Maintain before-and-after quantity records.
- Track movement reasons and associated users.

### 7. Customer Management
- Create and manage customer records.
- Store customer contact information.
- Update and deactivate customers.

### 8. Order Management
- Create customer orders with multiple products.
- Calculate order totals.
- Maintain order item price snapshots.
- Validate stock availability before order creation.
- Deduct inventory when orders are created.
- Support order status transitions.
- Restore inventory when eligible orders are cancelled.

### 9. Search, Filtering & Pagination
- Search products by name and SKU.
- Filter products by category and price.
- Search orders by customer information.
- Filter orders by status, customer and total amount.
- Sort and paginate product and order results.

### 10. Database Migrations
- Alembic-based database migrations.
- Automatic migration generation.
- Schema version management.

---

## Technology Stack

| Category | Technologies |
|---|---|
| Programming Language | Python 3.12 |
| Backend Framework | FastAPI |
| Database | MySQL 8.0 |
| ORM | SQLAlchemy |
| Data Validation | Pydantic |
| Authentication | JWT, bcrypt |
| Database Migrations | Alembic |
| Database Driver | PyMySQL |
| Testing | Pytest, HTTPX |
| API Documentation | Swagger UI |
| Version Control | Git, GitHub |

---

## Project Architecture

StockFlow follows a layered backend architecture to separate API handling, business logic, database operations and data validation.

```text
StockFlow/
│
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── endpoints/
│   │       │   ├── auth.py
│   │       │   ├── products.py
│   │       │   ├── categories.py
│   │       │   ├── suppliers.py
│   │       │   ├── inventory.py
│   │       │   ├── stock_movements.py
│   │       │   ├── customers.py
│   │       │   └── orders.py
│   │       └── router.py
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── dependencies.py
│   │   ├── permissions.py
│   │   └── security.py
│   │
│   ├── database/
│   │   └── session.py
│   │
│   ├── models/
│   ├── schemas/
│   ├── services/
│   └── main.py
│
├── alembic/
│   └── versions/
│
├── tests/
│
├── .env.example
├── .gitignore
├── alembic.ini
├── create_admin.py
├── requirements.txt
├── requirements-dev.txt
└── run.bat
```

### Architecture responsibilities

- **API Layer:** Handles HTTP requests, responses, authentication dependencies and permissions.
- **Service Layer:** Implements business rules and application logic.
- **Models Layer:** Defines database tables and relationships using SQLAlchemy.
- **Schemas Layer:** Validates incoming data and structures API responses using Pydantic.
- **Core Layer:** Handles configuration, security, authentication and authorization.
- **Database Layer:** Manages SQLAlchemy engine and database sessions.
- **Tests:** Contains automated tests for application functionality.

---

## Installation & Setup

### Prerequisites

Install the following before starting:

- Python 3.12
- MySQL Server 8.0
- Git

### 1. Clone the repository

```bash
git clone https://github.com/Khizer220/StockFlow.git
cd StockFlow
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate it on Windows:

```cmd
.venv\Scripts\activate
```

### 3. Install dependencies

For application runtime:

```bash
python -m pip install -r requirements.txt
```

For development and testing:

```bash
python -m pip install -r requirements-dev.txt
```

### 4. Create the MySQL database

Open MySQL and execute:

```sql
CREATE DATABASE stockflow_db;
```

### 5. Configure environment variables

Create a `.env` file in the project root by copying `.env.example`.

```cmd
copy .env.example .env
```

Update the values in `.env`:

```env
# Database Configuration
DB_HOST=localhost
DB_PORT=3306
DB_NAME=stockflow_db
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password

# JWT Configuration
JWT_SECRET_KEY=your_secure_secret_key
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Replace the placeholder values with your own database credentials and a securely generated JWT secret.

**Important:** Never commit your actual `.env` file or expose your database password or JWT secret.

### 6. Run database migrations

Apply all database migrations:

```bash
alembic upgrade head
```

### 7. Create an administrator account

Run:

```bash
python create_admin.py
```

Follow the prompts to create your initial administrator account.

### 8. Start the application

Run:

```bash
python -m uvicorn app.main:app --reload
```

Alternatively, on Windows, double-click `run.bat`.

The application will be available at:

```text
http://127.0.0.1:8000
```

---

## API Documentation

StockFlow provides interactive API documentation through Swagger UI.

Once the application is running, open:

**Swagger UI:** http://127.0.0.1:8000/docs

**ReDoc:** http://127.0.0.1:8000/redoc

**Health Check:** http://127.0.0.1:8000/health

### API Base URL

```text
http://127.0.0.1:8000/api/v1
```

### Main API Endpoints

| Module | Base Endpoint |
|---|---|
| Authentication | `/auth` |
| Products | `/products` |
| Categories | `/categories` |
| Suppliers | `/suppliers` |
| Inventory | `/inventory` |
| Stock Movements | `/stock-movements` |
| Customers | `/customers` |
| Orders | `/orders` |

Most protected endpoints require a valid JWT access token.

---

## Testing

StockFlow uses Pytest for automated testing.

A separate MySQL database is used for tests to isolate test data from application data.

Create the test database in MySQL:

```sql
CREATE DATABASE stockflow_test_db;
```

Run the complete test suite:

```bash
python -m pytest
```

Run tests with detailed output:

```bash
python -m pytest -v
```

Run tests for an individual module:

```bash
python -m pytest tests/test_products.py -v
```

### Current Test Coverage

| Module | Tests |
|---|---:|
| Authentication | 5 |
| Categories | 7 |
| Customers | 6 |
| Health | 1 |
| Inventory | 4 |
| Orders | 10 |
| Products | 6 |
| Stock Movements | 5 |
| Suppliers | 6 |
| **Total** | **50** |

**Latest verified result: 50 tests passed.**

The test configuration recreates tables in `stockflow_test_db`. Never configure this test database to point to production data.

---

## Database Management

StockFlow uses MySQL with SQLAlchemy ORM.

Alembic manages database schema changes.

Create a new migration:

```bash
alembic revision --autogenerate -m "describe your changes"
```

Apply migrations:

```bash
alembic upgrade head
```

Check the current migration:

```bash
alembic current
```

View migration history:

```bash
alembic history
```

---

## Security & Business Logic

The project incorporates several backend security and data-integrity practices:

- JWT-based authentication.
- Password hashing with bcrypt.
- Admin and Staff role-based authorization.
- Pydantic request validation.
- Database uniqueness and check constraints.
- Transactional order creation and cancellation.
- Stock validation before order processing.
- Database row locking for critical inventory operations.
- Rollback handling for failed transactions.
- Separate test database.

---

## Future Enhancements

Potential improvements for future development include:

- Docker and Docker Compose deployment.
- Cloud deployment and CI/CD integration.
- Automated low-stock notifications.
- Advanced inventory and sales analytics.
- Exportable inventory and order reports.
- Improved audit logging.
- Automated API performance testing.

---

## Author

**Syed Mustafa**

GitHub: https://github.com/Khizer220

---

## License

This project is currently maintained as a personal development project.
