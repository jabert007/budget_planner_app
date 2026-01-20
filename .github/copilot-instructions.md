# Budget Planner App - AI Coding Agent Instructions

## Architecture Overview

This is a **Streamlit-based personal finance application** with MySQL backend. The app implements a 50/30/20 budget allocation model (needs/wants/culture + unexpected).

### Core Components
- **app.py**: Login/Register UI (placeholder with hardcoded credentials)
- **test/test1.py**: Main application logic with full feature implementation
- **db_config.py**: MySQL connection management via `.streamlit/secrets.toml`
- **utils.py**: Password hashing utilities using werkzeug
- **schema.sql**: Database schema with 4 tables (users, goals, budget_allocation, daily_expenses)
- **functions/**: Directory for future modular functions (currently empty)
- **views/**: Directory for future multi-page views (currently empty)

### Data Flow
1. **Authentication**: Phone or email + password/PIN → users table
2. **Goal Setting**: Monthly saving target + yearly goal → goals table
3. **Budget Planning**: Monthly allocation across 4 categories (JSON-stored) → budget_allocation table
4. **Expense Tracking**: Daily expenses by category → daily_expenses table

## Critical Developer Workflows

### Setup & Execution
```bash
# First-time setup
pip install -r requirements.txt
mysql -u root -p < schema.sql  # Create database and tables

# Create .streamlit/secrets.toml with:
# [mysql]
# host = "localhost"
# user = "root"
# password = "your_mysql_password"
# database = "budget_planner"

# Run the app
streamlit run test/test1.py  # Main app is in test/ directory
streamlit run app.py         # Login/register placeholder
```

### Database Connection Pattern
All database queries must:
1. Use `get_connection()` from `db_config.py` to get fresh MySQL connector
2. Use `cursor(dictionary=True)` for dict-based field access
3. Call `conn.commit()` after INSERT/UPDATE/DELETE
4. Handle `mysql.connector.IntegrityError` for duplicate key violations (phone/email uniqueness)

Example (from test1.py):
```python
conn = get_connection()
cur = conn.cursor(dictionary=True)
cur.execute("INSERT INTO users (phone, email, password_hash, pin) VALUES (%s,%s,%s,%s)",
            (phone, email, hash_password(password), pin))
conn.commit()
```

## Project-Specific Patterns & Conventions

### Authentication Model
- Users can login via phone OR email (checked in WHERE clause)
- Supports both password (hashed with werkzeug) and PIN (plaintext stored)
- Session state tracked in `st.session_state` (logged_in, user_id, username)

### Budget Data Storage
- Budget allocations stored as **JSON in MySQL** (not normalized columns)
- Example: `needs`, `wants`, `culture`, `unexpected` are JSON serialized
- When updating, use `ON DUPLICATE KEY UPDATE` for month-based idempotency (see test1.py line ~100)

### UI Styling Patterns
- **app.py** demonstrates Streamlit CSS customization:
  - Hide default UI with style tags
  - Custom card styling with gradients
  - Custom button styling with CSS classes
  - Material Design color scheme (blue gradients)
- Use `st.set_page_config()` for page setup
- Use `st.markdown(..., unsafe_allow_html=True)` for custom HTML/CSS

### Password Security
- All passwords hashed with `werkzeug.generate_password_hash()`
- Verification with `werkzeug.check_password_hash()`
- Never store plaintext passwords (PIN is exception - architectural choice)

## Integration Points & External Dependencies

### MySQL Connector
- Library: `mysql-connector-python`
- Connection handled in `db_config.py:get_connection()`
- Secrets stored in `.streamlit/secrets.toml` (Streamlit best practice)

### External Libraries
- **streamlit**: UI framework
- **mysql-connector-python**: Database driver
- **werkzeug**: Password hashing
- **matplotlib**: Charting (imported in test1.py, not yet used)

### Key Database Constraints
- `users.phone` and `users.email` are UNIQUE
- Foreign keys enforce user_id references
- `daily_expenses.category` is ENUM ('needs','wants','culture','unexpected')

## Important Notes for AI Agents

1. **Main app is in test/test1.py**, not app.py. The app.py is a placeholder with hardcoded login ("admin"/"admin").
2. **Multi-page migration in progress**: functions/ and views/ directories exist but are empty—intended for future architectural refactoring.
3. **Budget JSON storage**: Don't normalize—maintain JSON format in database to match existing schema.
4. **Testing pattern**: test/test1.py serves as both test file and main app. Consider creating separate test files in future.
5. **Frontend/Mobile roadmap**: README mentions converting to Android/iOS via WebView or PWA once deployed online.
