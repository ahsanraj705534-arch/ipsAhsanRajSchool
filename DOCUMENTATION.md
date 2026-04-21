# Indian Public School Portal Documentation

## Overview

This project is a Flask-based student management portal for **Indian Public School**, Rasulpur Dabheri, Budhana, Muzaffarnagar, Uttar Pradesh, India.

The website supports:

- Public student-side registration
- Admin login
- Class-wise student record management
- Search and filtering
- Edit, delete, and print student details
- Excel export
- Mobile-friendly admin and form screens

## Technology Stack

- Backend: Flask
- ORM: Flask-SQLAlchemy / SQLAlchemy
- Database: MySQL or SQLite fallback
- Excel export: openpyxl
- Frontend: HTML, CSS, JavaScript

## Project Structure

```text
indian_Public_School/
|-- app.py
|-- requirements.txt
|-- README.md
|-- DOCUMENTATION.md
|-- templates/
|   |-- base.html
|   |-- home.html
|   |-- login.html
|   |-- student_form.html
|   |-- students.html
|   |-- student_detail.html
|   |-- student_print.html
|   |-- contact.html
|   |-- 404.html
|-- static/
|   |-- css/styles.css
|   |-- js/app.js
|   |-- images/
|-- data/
|-- instance/
```

## Main Features

### 1. Homepage

- School name, logo, and address
- School information blocks and gallery
- Student registration CTA
- Admin login / dashboard CTA
- Class-wise quick links

### 2. Student Registration

Public route:

- `/student-registration`

Fields included:

- Student Name
- Father's Name
- Mother's Name
- Date of Birth
- Gender
- Class
- Section
- Mobile Number
- Address

Validation includes:

- required fields
- valid date
- valid gender and class
- 10-digit mobile number
- section format check

### 3. Admin Dashboard

Admin route:

- `/students`

Features:

- View all students
- Search by name, parent name, student ID, or mobile
- Filter by class and section
- Quick class-wise access
- Mobile-optimized card view
- Bottom mobile action bar

### 4. Student Record Actions

- Add student: `/students/add`
- View student: `/students/<id>`
- Edit student: `/students/<id>/edit`
- Delete student: `/students/<id>/delete`
- Print student: `/students/<id>/print`

### 5. Export to Excel

- Route: `/students/export`
- Output format: `.xlsx`

## Authentication

Admin login route:

- `/login`

Default credentials:

- Username: `admin`
- Password: `admin123`

For production, set:

```powershell
$env:ADMIN_USERNAME="your-admin-name"
$env:ADMIN_PASSWORD="your-strong-password"
```

## Database Configuration

The application supports these database options in this order:

1. `DATABASE_URL`
2. MySQL environment variables
3. SQLite fallback

### MySQL Environment Variables

```powershell
$env:MYSQL_HOST="localhost"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="your-password"
$env:MYSQL_DB="indian_public_school"
```

### Direct Database URL

```powershell
$env:DATABASE_URL="mysql+pymysql://root:password@localhost:3306/indian_public_school"
```

### SQLite Fallback

If no MySQL settings are provided, the app uses:

- `data/school.db`

## Installation

### Recommended

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python app.py
```

### Current Local Machine Note

If your default `python` command points to the wrong interpreter on Windows, use:

```powershell
& "C:\Users\Atique Rana\AppData\Local\Programs\Python\Python311\python.exe" app.py
```

If your PowerShell profile has already been updated, plain `python app.py` should work in a new PowerShell session.

## Important Routes

- `/` Home page
- `/contact` Contact page
- `/login` Admin login
- `/logout` Admin logout
- `/student-registration` Public student submission
- `/students` Admin dashboard
- `/students/add` Add student
- `/students/export` Download Excel

## Mobile-Friendly Improvements

The current project includes mobile-specific enhancements:

- responsive header and navigation
- mobile-friendly homepage sections
- dashboard card layout on small screens
- sticky bottom action bars on mobile
- grouped mobile sections in student form
- grouped mobile sections in student detail view

## Production Recommendations

Before deploying publicly:

1. Change the admin username and password.
2. Set a strong `SECRET_KEY`.
3. Use MySQL instead of SQLite for real deployment.
4. Run behind a production WSGI server such as Gunicorn, Waitress, or uWSGI.
5. Turn off Flask debug mode.
6. Use HTTPS in production.
7. Back up the database regularly.

## Production Environment Variables

Recommended:

```powershell
$env:SECRET_KEY="replace-with-a-long-random-secret"
$env:ADMIN_USERNAME="school-admin"
$env:ADMIN_PASSWORD="strong-password"
$env:MYSQL_HOST="localhost"
$env:MYSQL_PORT="3306"
$env:MYSQL_USER="root"
$env:MYSQL_PASSWORD="your-password"
$env:MYSQL_DB="indian_public_school"
```

## Running in Production

For a production server, avoid:

```powershell
python app.py
```

Instead use a proper WSGI server. Example with Waitress:

```powershell
pip install waitress
waitress-serve --host=0.0.0.0 --port=8000 app:app
```

## Troubleshooting

### `ModuleNotFoundError: No module named 'flask'`

Install dependencies:

```powershell
pip install -r requirements.txt
```

### `python` points to the wrong interpreter

Check:

```powershell
where python
python --version
```

### Database not connecting

Check:

- MySQL is running
- database exists
- credentials are correct
- environment variables are set in the same terminal session

### Excel export not downloading

Check:

- admin login is active
- student data exists
- browser download permissions are allowed

## School Content Notes

- The site currently uses Indian-student visuals stored in `static/images/`.
- If real school photos are provided later, replace those image files or update references in `templates/home.html`.
- School identity currently shown:
  - Name: Indian Public School
  - Address: Rasulpur Dabheri, Budhana, Muzaffarnagar, Uttar Pradesh, India
  - Motto in logo: `God is One`

## Maintenance Tasks

Common future improvements:

- add password hashing
- add CSRF protection
- add pagination to dashboard
- add audit logs for record changes
- add backup/export scheduling
- add role-based access if multiple staff users are needed
