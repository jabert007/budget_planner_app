# Budget Planner Streamlit App (Local MySQL)

## Setup Instructions

### 1. Prerequisites
- Python 3.9+
- MySQL installed locally
- Streamlit

### 2. MySQL Setup
```sql
CREATE DATABASE budget_planner;
USE budget_planner;
SOURCE schema.sql;
```

### 3. Streamlit Secrets
Create a file `.streamlit/secrets.toml` inside your project folder:

```toml
[mysql]
host = "localhost"
user = "root"
password = "your_mysql_password"
database = "budget_planner"
```

### 4. Run App
```bash
pip install -r requirements.txt
streamlit run app.py
```

### 5. Switch to Railway MySQL Later
Just replace values in `.streamlit/secrets.toml` with Railway credentials.

### 6. Convert to Android/iOS
- Deploy this Streamlit app online.
- Wrap the deployed URL in a WebView (Android Studio / Xcode) or make it a PWA.
