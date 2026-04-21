# Indian Public School Portal

Responsive Flask website for **Indian Public School**, Rasulpur Dabheri, Budhana, Muzaffarnagar, Uttar Pradesh, India.

## Documentation

- Full project guide: `DOCUMENTATION.md`

## Features

- Professional blue-and-white school-themed homepage
- Public student-side registration form
- Class-wise student storage and filtering
- Admin login for viewing, editing, deleting, and printing records
- Dashboard with search, section filter, and class quick access
- Excel export using `.xlsx`
- Student ID auto-generation

## Tech Stack

- Frontend: HTML, CSS, JavaScript
- Backend: Flask
- Database: MySQL supported via environment variables
- Local fallback: SQLite for quick local startup

## Install

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your values
python app.py
```

## Admin Login

- Username: `admin`
- Password: `admin123`

Change these in production using environment variables in `.env` file:

```env
ADMIN_USERNAME=your-admin-name
ADMIN_PASSWORD_HASH=run: python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your-password'))"
```

## Production Setup

Copy `.env.example` to `.env` and set environment variables for security:

```env
SECRET_KEY=your-very-long-random-secret-key
WTF_CSRF_SECRET_KEY=another-long-random-key
FLASK_ENV=production
ADMIN_USERNAME=admin
ADMIN_PASSWORD_HASH=hashed-password
DATABASE_URL=mysql+pymysql://user:pass@host/db
```

For production deployment, use a WSGI server like Gunicorn and reverse proxy with Nginx. Ensure HTTPS is enabled.

## Database Setup

The app supports either:

1. `DATABASE_URL`
2. MySQL environment variables
3. SQLite fallback if neither is configured

### MySQL Example

Create the database first:

```sql
CREATE DATABASE indian_public_school CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

Set environment variables:

```powershell
$env:MYSQL_HOST="localhost"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="your-password"
$env:MYSQL_DB="indian_public_school"
```

Then run:

```bash
python app.py
```

## Main Routes

- `/` Home page
- `/student-registration` Public student-side form
- `/login` Admin login
- `/students` Admin dashboard
- `/students/add` Admin add student
- `/students/export` Download Excel

## Notes

- The current school branding asset used in the site header is `static/images/logo.png`.
- If MySQL is not configured yet, the app will automatically use `data/school.db` locally.
