# 📦 StockFlow

**Inventory Management & Analytics System**

StockFlow is a Python-based inventory management web application designed to help small businesses manage product catalogs, monitor stock levels across warehouses, and track inventory movements.

The application uses PostgreSQL for relational data storage, Streamlit for its web interface, and Python for business logic and reporting.

## Application Preview

### Dashboard
![StockFlow Dashboard](docs/screenshots/dashboard.png)

### Product Management
![Product Management](docs/screenshots/products.png)

### Inventory Management
![Inventory Management](docs/screenshots/inventory.png)

### Stock Movements
![Stock Movements](docs/screenshots/movements.png)

### Reports & Analytics
![Reports and Analytics](docs/screenshots/reports.png)

## Features

- **Product Management:** Create, view, update, activate, and deactivate products.
- **Inventory Tracking:** Monitor product stock levels across multiple warehouses.
- **Stock Movements:** Register inventory entries and exits with transaction handling.
- **Stock Validation:** Prevent movements that would produce negative inventory.
- **Dashboard:** Visualize operational metrics, stock alerts, and recent movements.
- **Reports & Analytics:** Filter movements by date, product, warehouse, and movement type; export reports to CSV.
- **Automated Testing:** PostgreSQL integration tests using Pytest.

## Tech Stack

| Technology | Purpose |
|---|---|
| Python | Backend logic |
| PostgreSQL | Relational database |
| Psycopg 3 | PostgreSQL driver |
| Streamlit | Web interface |
| Pandas | Data processing and reporting |
| Pytest | Automated testing |
| Git | Version control |

## Architecture

StockFlow follows a modular structure:

- `app.py` — Application entry point and navigation
- `views/` — Streamlit user interface pages
- `database/` — SQL queries and business operations
- `tests/` — Automated integration tests
- `database/schema.sql` — Database schema
- `database/seed.sql` — Sample development data

## Local Installation

**Prerequisites:** Python, PostgreSQL, and Git.

1. Clone the repository and open the project directory.
2. Create and activate a Python virtual environment.
3. Install dependencies with `python -m pip install -r requirements.txt`.
4. Create a PostgreSQL database named `stockflow_db`.
5. Execute `database/schema.sql` against that database.
6. Optionally execute `database/seed.sql` to load sample data into an empty database.
7. Copy `.env.example` to `.env` and configure the database credentials.
8. Run the application using `python -m streamlit run app.py`.

The application normally runs at `http://localhost:8501`.

## Running Tests

Create a separate PostgreSQL database named `stockflow_test_db`, initialize its schema, and configure `.env.test`.

Run:

`python -m pytest tests/ -v`

**Warning:** Integration tests clear the tables in `stockflow_test_db`. Never use a database containing important information for automated tests.

## Design Considerations

- SQL parameters are used to separate query structure from user-supplied values.
- Stock entry and exit operations update inventory and movement history within database transactions.
- Row locking is used to protect inventory updates during concurrent operations.
- Products are deactivated instead of being physically deleted.
- Database credentials are stored outside the source code.

## Current Limitations

- Authentication and role-based permissions are not implemented.
- Initial inventory balances are loaded separately from movement history.
- Product minimum stock levels are shared across warehouses.
- Automated concurrency testing and deployment configuration are planned improvements.

## Future Improvements

- User authentication and authorization
- Warehouse-to-warehouse transfers
- Product-specific minimum stock levels per warehouse
- Opening balance movement records
- Extended automated test coverage
- Cloud deployment

## Project Status

**MVP — Local development.**

This project was developed as a software engineering portfolio project using fictional business data.