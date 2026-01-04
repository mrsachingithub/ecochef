# EcoChef

EcoChef is a food waste reduction and delivery management platform.

## Technologies & Tools Used

### Backend
*   **Python**: Core programming language.
*   **Flask**: Lightweight web framework for building the application.
*   **Flask-SQLAlchemy**: ORM for database management.
*   **Flask-Migrate**: Extension for handling database migrations.
*   **Flask-Login**: Manages user authentication and sessions.

### Data & Machine Learning
*   **Pandas**: For data manipulation and analysis.
*   **Scikit-Learn**: Used for predictive modeling or data analysis features.

### Database
*   **SQLite**: Default database for local development.
*   **PostgreSQL**: Recommended production database (via `psycopg2-binary`).

### Deployment
*   **Gunicorn**: WSGI HTTP Server for production.
*   **Render**: Cloud platform for hosting the web service and database.

## Deployment on Render

This project is configured for deployment on **Render**.

### 1. Push to GitHub
Ensure this project is pushed to a GitHub repository.

### 2. Create Web Service on Render
1.  Log in to the [Render Dashboard](https://dashboard.render.com/).
2.  Click **New +** and select **Web Service**.
3.  Connect your GitHub account and select this repository.

### 3. Configure the Service
Render will auto-detect some settings, but ensure the following:
*   **Name**: Choose a name (e.g., `ecochef-app`).
*   **Runtime**: `Python 3`
*   **Build Command**: `pip install -r requirements.txt`
*   **Start Command**: `gunicorn run:app`

### 4. Database Setup (Important)
Since this app uses a database, you must set up a persistent database on Render to prevent data loss when the app restarts.

1.  **Create a PostgreSQL Database**:
    *   On the Render Dashboard, click **New +** -> **PostgreSQL**.
    *   Name it (e.g., `ecochef-db`).
    *   Copy the **Internal Database URL** once it's created.

2.  **Connect App to Database**:
    *   Go back to your **Web Service** settings.
    *   Click on **Environment Variables**.
    *   Add a new variable:
        *   **Key**: `DATABASE_URL`
        *   **Value**: (Paste the Internal Database URL you copied)
    *   Add another variable for security:
        *   **Key**: `SECRET_KEY`
        *   **Value**: (Generate a random string, e.g., `super-secret-key-123`)

### 5. Deploy
Click **Create Web Service** (or **Save Changes**). Render will build and deploy your app. properly.
