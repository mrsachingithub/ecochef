# EcoChef

EcoChef is a food waste reduction and delivery management platform designed to help restaurants optimize their operations. By tracking daily food preparation, sales, and waste, EcoChef provides actionable insights to minimize financial loss and environmental impact.

## Key Features

*   **Waste Tracking & Analytics**: Comprehensive logging system to track prepared vs. sold items, automatically calculating waste quantity and cost impact.
*   **Order Management**: specific workflows for handling delivery orders from placement to completion.
*   **Inventory Control**: Manage food items, categories, and unit costs to maintain accurate financial data.
*   **Role-Based Access Control**: Secure authentication with distinct roles for Administrators, Staff, and Delivery personnel.

## Technologies & Tools Used

### Backend
*   **Python**: Core programming language.
*   **Flask**: Lightweight web framework for building the application.
*   **Flask-SQLAlchemy**: ORM for robust database management.
*   **Flask-Login**: Secure user session management.
*   **Flask-Migrate**: Handling database schema migrations.

### Data & Analytics
*   **Pandas**: High-performance data manipulation and analysis.
*   **Scikit-Learn**: Integrated for predictive modeling and data insights.

### Database
*   **PostgreSQL**: Production-grade relational database.
*   **SQLite**: Lightweight database for development environments.

### Deployment / Infrastructure
*   **Gunicorn**: Production WSGI HTTP Server.
*   **Render**: Cloud platform for hosting the web service and database.
