import io
import logging
import os
import re
from copy import deepcopy
from datetime import date, datetime
from functools import wraps
from pathlib import Path
from urllib.parse import quote_plus, urlparse

from dotenv import load_dotenv
from flask import (
    Flask,
    flash,
    redirect,
    render_template,
    request,
    send_file,
    session,
    url_for,
)
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect, generate_csrf
from openpyxl import Workbook
from sqlalchemy import func, or_
from werkzeug.security import check_password_hash, generate_password_hash

load_dotenv()


CLASS_OPTIONS = [
    "Nursery",
    "LKG",
    "UKG",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "10",
    "11",
    "12",
]
GENDER_OPTIONS = ["Male", "Female", "Other"]
SECTION_SUGGESTIONS = ["A", "B", "C", "D", "E", "F", "G", "H"]
NAME_PATTERN = re.compile(r"^[A-Za-z][A-Za-z .'-]{1,118}$")
PUBLIC_EDIT_SESSION_KEY = "public_edit_student_id"
HOME_PAGE_CONTENT = {
    "hero": {
        "eyebrow": "God is One | Indian Public School",
        "headline": "Indian Public School, Rasulpur Dabheri, Budhana",
        "description": (
            "This website presents Indian Public School and supports school "
            "administration through student registration, class-wise records, "
            "student profiles, and Excel export."
        ),
        "highlights": [
            "Location: Budhana, Muzaffarnagar, Uttar Pradesh",
            "Official IPS identity and motto on the homepage",
            "Class-wise digital student record management",
        ],
        "image": "images/students-hero.jpg",
        "image_alt": "Indian students in school uniform standing confidently together.",
    },
    "about": {
        "title": "Indian Public School Overview",
        "intro": (
            "Indian Public School is located at Rasulpur Dabheri, Budhana, "
            "Muzaffarnagar, Uttar Pradesh, India. It blends strong academic standards "
            "with values-based learning and community involvement."
        ),
        "description": (
            "The official school identity shown on this website uses the IPS logo and "
            "the motto 'God is One'. The portal is designed to support admissions, "
            "student record management, and transparent school-family communication."
        ),
        "points": [
            "Official school name: Indian Public School",
            "Campus located at Rasulpur Dabheri, Budhana, Muzaffarnagar, Uttar Pradesh",
            "Motto shown in the school logo: God is One",
            "Academic and co-curricular learning supported by local teacher leadership",
        ],
    },
    "school_details": {
        "heading": "School Details",
        "title": "What makes Indian Public School special",
        "points": [
            {
                "title": "Experienced local faculty",
                "description": "A dedicated team of teachers supports strong academic progress and moral development."
            },
            {
                "title": "Balanced student development",
                "description": "The school emphasizes discipline, confidence, and practical learning along with good behavior."
            },
            {
                "title": "Safe and welcoming campus",
                "description": "Students learn in a supportive environment designed for focus, hygiene, and safety."
            },
            {
                "title": "Community-driven values",
                "description": "Parents, teachers, and local leaders collaborate to build a stronger school culture."
            },
        ],
    },
    "school_timings": {
        "heading": "School Timings",
        "title": "Daily time schedule for students and school activities",
        "points": [
            {
                "label": "Morning Reporting",
                "title": "Arrival and assembly",
                "description": (
                    "Students should reach the campus on time so attendance, prayer, and morning assembly can begin smoothly."
                ),
            },
            {
                "label": "Teaching Hours",
                "title": "Regular class sessions",
                "description": (
                    "Daily academic periods are planned for focused classroom learning, revision, and guided subject practice."
                ),
            },
            {
                "label": "Break and Activity Time",
                "title": "Balanced school routine",
                "description": (
                    "The school day includes time for short breaks, discipline routines, and student activity support."
                ),
            },
            {
                "label": "Office Support",
                "title": "Admin and parent queries",
                "description": (
                    "School staff can use office hours for student record updates, admission help, and class-wise administrative work."
                ),
            },
        ],
    },
    "admission_steps": {
        "heading": "Admission Journey",
        "title": "How parents and students can complete registration",
        "points": [
            {
                "title": "Open the Student Form",
                "description": (
                    "Parents or guardians can start the process directly from the website using the student registration page."
                ),
            },
            {
                "title": "Fill Accurate Student Details",
                "description": (
                    "Enter the student name, parents' names, date of birth, class, section, mobile number, and address carefully."
                ),
            },
            {
                "title": "School Reviews The Record",
                "description": (
                    "The submitted record becomes available in the admin dashboard so school staff can verify and manage it class-wise."
                ),
            },
            {
                "title": "Update And Export Anytime",
                "description": (
                    "The school office can edit records, print profiles, and export Excel sheets whenever reporting or updates are needed."
                ),
            },
        ],
    },
    "facilities": [
        {
            "title": "Student Registration Form",
            "description": (
                "Students or guardians can submit admission and student information "
                "directly from the website."
            ),
        },
        {
            "title": "Class-wise Record Access",
            "description": (
                "Every saved student entry is organized by class and section for faster "
                "school-office access."
            ),
        },
        {
            "title": "Editable Student Records",
            "description": (
                "Admin staff can open student records, edit information, and keep the "
                "database up to date."
            ),
        },
        {
            "title": "Printable Student Profiles",
            "description": (
                "Each record includes a clean print view for student details whenever "
                "the school office needs paper copies."
            ),
        },
        {
            "title": "Excel Export",
            "description": (
                "All student data can be downloaded in Excel format for reporting and "
                "administrative work."
            ),
        },
        {
            "title": "Admin Login Access",
            "description": (
                "The portal includes a protected admin side for record management, "
                "searching, filtering, and dashboard use."
            ),
        },
    ],
    "why_choose_us": [
        {
            "title": "One Place for Student Data",
            "description": (
                "The website keeps student registration and record handling in one "
                "centralized system."
            ),
        },
        {
            "title": "Faster Class-wise Access",
            "description": (
                "Staff can quickly open the right class list instead of searching "
                "through scattered records."
            ),
        },
        {
            "title": "Better Admin Workflow",
            "description": (
                "Search, filters, edit tools, print view, and export keep the office "
                "workflow cleaner and easier."
            ),
        },
        {
            "title": "Mobile-Friendly Access",
            "description": (
                "The layout works better on phones so staff and families can use the "
                "portal comfortably on smaller screens."
            ),
        },
    ],
    "achievements": {
        "heading": "Achievements and Results",
        "title": "How the school supports student progress and outcomes",
        "points": [
            {
                "title": "Regular academic review",
                "description": (
                    "Students are guided through class-wise learning progress so teachers can track improvement and support better results."
                ),
            },
            {
                "title": "Concept clarity and practice",
                "description": (
                    "Strong focus on subject understanding, revision, and daily practice helps students build confidence in examinations."
                ),
            },
            {
                "title": "Recognition of discipline and effort",
                "description": (
                    "The school encourages good behavior, attendance, and sincere effort as part of student achievement."
                ),
            },
            {
                "title": "Parent-school transparency",
                "description": (
                    "Clear student records and organized data help families and staff follow student progress more effectively."
                ),
            },
        ],
    },
    "gallery": [
        {
            "image": "images/students-group.jpg",
            "alt": "Indian school boys in uniform during a school assembly.",
            "label": "Student Assembly",
            "caption": "Indian students in uniform gathered during a school event.",
        },
        {
            "image": "images/students-classroom.jpg",
            "alt": "Indian schoolgirls listening carefully in a classroom.",
            "label": "Classroom Focus",
            "caption": "Indian students in a classroom learning environment.",
        },
        {
            "image": "images/students-outdoor-study.jpg",
            "alt": "Portrait of a young Indian student in school uniform.",
            "label": "Student Portrait",
            "caption": "A stronger student-focused visual for the school homepage.",
        },
    ],
}
CONTACT_PAGE_CONTENT = {
    "office": {
        "title": "School location and office access",
        "description": (
            "Reach the school office easily, open the campus location in Google Maps, "
            "and use the leadership contact buttons for direct communication."
        ),
        "address_label": "School Address",
        "map_label": "Open Google Maps",
    },
    "leaders": [
        {
            "role": "Principal",
            "eyebrow": "Academic Leadership",
            "name": "Ahsan Sir",
            "image": "images/principal-ahsan.svg",
            "image_alt": "Portrait placeholder for Principal Ahsan Sir",
            "summary": (
                "Ahsan Sir leads the school with a strong academic background in "
                "Mathematics and Physics. He encourages disciplined study, concept "
                "clarity, and confident learning habits in the classroom."
            ),
            "highlights": [
                {
                    "title": "Subject Strength",
                    "description": "Mathematics and Physics",
                },
                {
                    "title": "Teaching Style",
                    "description": (
                        "Clear concepts, logical thinking, and regular student guidance."
                    ),
                },
                {
                    "title": "About The Teacher",
                    "description": (
                        "He motivates students to stay curious, practice regularly, "
                        "and build strong academic fundamentals with confidence."
                    ),
                },
            ],
            "mobile_number": "+91 7055341433",
            "email": "ahsan@example.com",
        },
        {
            "role": "Manager",
            "eyebrow": "School Management",
            "name": "Najim Sir",
            "image": "images/manager-najim.svg",
            "image_alt": "Portrait placeholder for Manager Najim Sir",
            "summary": (
                "Najim Sir supports the school with a Science-focused outlook and "
                "practical guidance. He helps create an organized, student-friendly "
                "environment where learning and administration move smoothly together."
            ),
            "highlights": [
                {
                    "title": "Subject Strength",
                    "description": "Science",
                },
                {
                    "title": "Work Focus",
                    "description": (
                        "School management, student support, and a balanced learning atmosphere."
                    ),
                },
                {
                    "title": "About The Teacher",
                    "description": (
                        "He encourages practical understanding, steady discipline, "
                        "and positive support so students can grow with confidence."
                    ),
                },
            ],
            "mobile_number": "+91 XXXXXXXXXX",
            "email": "najim@example.com",
        },
    ],
}


def build_database_uri() -> str:
    database_url = os.getenv("DATABASE_URL", "").strip()
    if database_url:
        if database_url.startswith("mysql://"):
            return database_url.replace("mysql://", "mysql+pymysql://", 1)
        return database_url

    mysql_host = os.getenv("MYSQL_HOST", "").strip()
    mysql_port = os.getenv("MYSQL_PORT", "3306").strip()
    mysql_user = os.getenv("MYSQL_USER", "").strip()
    mysql_password = os.getenv("MYSQL_PASSWORD", "").strip()
    mysql_db = os.getenv("MYSQL_DB", "").strip()

    if all([mysql_host, mysql_user, mysql_db]):
        auth = quote_plus(mysql_user)
        if mysql_password:
            auth = f"{auth}:{quote_plus(mysql_password)}"
        return (
            f"mysql+pymysql://{auth}@{mysql_host}:{mysql_port}/{mysql_db}"
            "?charset=utf8mb4"
        )

    project_root = Path(__file__).resolve().parent
    data_dir = project_root / "data"
    data_dir.mkdir(exist_ok=True)
    sqlite_path = (data_dir / "school.db").as_posix()
    return f"sqlite:///{sqlite_path}"


app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "indian-public-school-change-this-secret")
app.config["WTF_CSRF_SECRET_KEY"] = os.getenv("WTF_CSRF_SECRET_KEY", os.getenv("SECRET_KEY", "csrf-secret"))
app.config["SQLALCHEMY_DATABASE_URI"] = build_database_uri()
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SESSION_COOKIE_SECURE"] = os.getenv("FLASK_ENV") == "production"
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"
db = SQLAlchemy(app)
csrf = CSRFProtect(app)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class Student(db.Model):
    __tablename__ = "students"

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.String(24), unique=True, nullable=False, index=True)
    student_name = db.Column(db.String(120), nullable=False)
    father_name = db.Column(db.String(120), nullable=False)
    mother_name = db.Column(db.String(120), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    gender = db.Column(db.String(20), nullable=False)
    student_class = db.Column(db.String(20), nullable=False, index=True)
    section = db.Column(db.String(10), nullable=False, index=True)
    mobile_number = db.Column(db.String(10), nullable=False)
    address = db.Column(db.String(300), nullable=False)
    submission_source = db.Column(db.String(20), nullable=False, default="admin")
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(
        db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow
    )


def admin_username() -> str:
    return os.getenv("ADMIN_USERNAME", "admin")


def admin_password_hash() -> str:
    # In production, set ADMIN_PASSWORD_HASH to the hashed value
    # For development, hash the default password
    default_hash = generate_password_hash("admin123")
    return os.getenv("ADMIN_PASSWORD_HASH", default_hash)


def safe_next_url(target: str | None) -> str:
    if not target:
        return url_for("view_students")

    parsed = urlparse(target)
    if parsed.netloc or not target.startswith("/"):
        return url_for("view_students")
    return target


def login_required(view):
    @wraps(view)
    def wrapped_view(*args, **kwargs):
        if not session.get("admin_logged_in"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)

    return wrapped_view


def generate_student_identifier() -> str:
    prefix = f"IPS{datetime.now().year}"
    latest_student = (
        Student.query.filter(Student.student_id.like(f"{prefix}%"))
        .order_by(Student.id.desc())
        .first()
    )

    next_number = 1
    if latest_student and latest_student.student_id[-4:].isdigit():
        next_number = int(latest_student.student_id[-4:]) + 1

    return f"{prefix}{next_number:04d}"


def validate_student_form(form_data):
    cleaned_data = {
        "student_name": form_data.get("student_name", "").strip(),
        "father_name": form_data.get("father_name", "").strip(),
        "mother_name": form_data.get("mother_name", "").strip(),
        "date_of_birth": form_data.get("date_of_birth", "").strip(),
        "gender": form_data.get("gender", "").strip(),
        "student_class": form_data.get("student_class", "").strip(),
        "section": form_data.get("section", "").strip().upper(),
        "mobile_number": re.sub(r"\D", "", form_data.get("mobile_number", "")),
        "address": form_data.get("address", "").strip(),
    }
    errors = []

    required_fields = {
        "student_name": "Student name",
        "father_name": "Father's name",
        "mother_name": "Mother's name",
        "date_of_birth": "Date of birth",
        "gender": "Gender",
        "student_class": "Class",
        "section": "Section",
        "mobile_number": "Mobile number",
        "address": "Address",
    }

    for field_name, label in required_fields.items():
        if not cleaned_data[field_name]:
            errors.append(f"{label} is required.")

    for field_name, label in (
        ("student_name", "Student name"),
        ("father_name", "Father's name"),
        ("mother_name", "Mother's name"),
    ):
        value = cleaned_data[field_name]
        if value and not NAME_PATTERN.match(value):
            errors.append(f"{label} should contain only letters and basic punctuation.")

    try:
        parsed_dob = datetime.strptime(cleaned_data["date_of_birth"], "%Y-%m-%d").date()
        if parsed_dob > date.today():
            errors.append("Date of birth cannot be in the future.")
    except ValueError:
        parsed_dob = None
        errors.append("Date of birth must be a valid date.")

    if cleaned_data["gender"] and cleaned_data["gender"] not in GENDER_OPTIONS:
        errors.append("Please choose a valid gender option.")

    if cleaned_data["student_class"] and cleaned_data["student_class"] not in CLASS_OPTIONS:
        errors.append("Please choose a valid class.")

    if cleaned_data["section"] and not re.match(r"^[A-Z0-9-]{1,5}$", cleaned_data["section"]):
        errors.append("Section must be 1 to 5 characters using letters, numbers, or hyphens.")

    if cleaned_data["mobile_number"] and not re.match(r"^\d{10}$", cleaned_data["mobile_number"]):
        errors.append("Mobile number must contain exactly 10 digits.")

    if len(cleaned_data["address"]) > 300:
        errors.append("Address must be 300 characters or fewer.")

    if parsed_dob:
        cleaned_data["date_of_birth"] = parsed_dob

    return cleaned_data, errors


def validate_public_edit_lookup(form_data):
    lookup_values = {
        "student_id": form_data.get("student_id", "").strip().upper(),
        "mobile_number": re.sub(r"\D", "", form_data.get("mobile_number", "")),
    }
    errors = []

    if not lookup_values["student_id"]:
        errors.append("Student ID is required.")

    if not lookup_values["mobile_number"]:
        errors.append("Mobile number is required.")
    elif not re.match(r"^\d{10}$", lookup_values["mobile_number"]):
        errors.append("Mobile number must contain exactly 10 digits.")

    return lookup_values, errors


def student_form_payload(cleaned_data):
    return {
        "student_name": cleaned_data["student_name"],
        "father_name": cleaned_data["father_name"],
        "mother_name": cleaned_data["mother_name"],
        "date_of_birth": cleaned_data["date_of_birth"],
        "gender": cleaned_data["gender"],
        "student_class": cleaned_data["student_class"],
        "section": cleaned_data["section"],
        "mobile_number": cleaned_data["mobile_number"],
        "address": cleaned_data["address"],
    }


def find_duplicate_student(cleaned_data, exclude_student_pk=None):
    if not isinstance(cleaned_data.get("date_of_birth"), date):
        return None

    duplicate_query = Student.query.filter(
        func.lower(Student.student_name) == cleaned_data["student_name"].lower(),
        func.lower(Student.father_name) == cleaned_data["father_name"].lower(),
        func.lower(Student.mother_name) == cleaned_data["mother_name"].lower(),
        Student.date_of_birth == cleaned_data["date_of_birth"],
    )

    if exclude_student_pk is not None:
        duplicate_query = duplicate_query.filter(Student.id != exclude_student_pk)

    return duplicate_query.order_by(Student.id.asc()).first()


def duplicate_student_message(student):
    return (
        "A student with the same name, parents' names, and date of birth already "
        f"exists under ID {student.student_id} in Class {student.student_class} - "
        f"Section {student.section}."
    )


def apply_student_form_data(student, cleaned_data):
    for field_name, value in student_form_payload(cleaned_data).items():
        setattr(student, field_name, value)


def normalize_student_identifier(student_id: str) -> str:
    return student_id.strip().upper()


def authorize_public_student_edit(student_id: str):
    session[PUBLIC_EDIT_SESSION_KEY] = normalize_student_identifier(student_id)


def clear_public_student_edit():
    session.pop(PUBLIC_EDIT_SESSION_KEY, None)


def public_student_edit_is_authorized(student_id: str) -> bool:
    return session.get(PUBLIC_EDIT_SESSION_KEY) == normalize_student_identifier(
        student_id
    )


def build_contact_page_content():
    contact_page = deepcopy(CONTACT_PAGE_CONTENT)
    office_address = (
        "Indian Public School, Rasulpur Dabheri, Budhana, Muzaffarnagar, Uttar Pradesh, India"
    )

    contact_page["office"]["address"] = office_address
    contact_page["office"]["map_url"] = (
        "https://www.google.com/maps/search/?api=1&query="
        f"{quote_plus(office_address)}"
    )

    for leader in contact_page["leaders"]:
        digits = re.sub(r"\D", "", leader["mobile_number"])
        leader["phone_ready"] = len(digits) >= 10
        leader["email_ready"] = bool(leader["email"] and "@" in leader["email"])

        if leader["phone_ready"]:
            leader["call_url"] = f"tel:+{digits}"
            leader["whatsapp_url"] = f"https://wa.me/{digits}"
        else:
            leader["call_url"] = "#"
            leader["whatsapp_url"] = "#"
        leader["email_url"] = f"mailto:{leader['email']}" if leader["email_ready"] else "#"

    return contact_page


@app.context_processor
def inject_school_context():
    return {
        "school_info": {
            "name": "Indian Public School",
            "tagline": "Centralized student registration and record management",
            "address": "Rasulpur Dabheri, Budhana, Muzaffarnagar, Uttar Pradesh, India",
        },
        "class_options": CLASS_OPTIONS,
        "gender_options": GENDER_OPTIONS,
        "section_suggestions": SECTION_SUGGESTIONS,
        "current_year": datetime.now().year,
        "csrf_token": generate_csrf(),
    }


@app.route("/")
def home():
    total_students = Student.query.count()
    class_count = db.session.query(Student.student_class).distinct().count()
    class_summary = (
        db.session.query(Student.student_class, func.count(Student.id))
        .group_by(Student.student_class)
        .order_by(Student.student_class.asc())
        .all()
    )
    return render_template(
        "home.html",
        total_students=total_students,
        class_count=class_count,
        class_summary=class_summary,
        class_totals={class_name: total for class_name, total in class_summary},
        homepage_content=HOME_PAGE_CONTENT,
        contact_page=build_contact_page_content(),
    )


@app.route("/contact")
def contact():
    return render_template("contact.html", contact_page=build_contact_page_content())


@app.route("/documentation")
def documentation():
    return render_template("documentation.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    next_url = safe_next_url(request.args.get("next"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        next_url = safe_next_url(request.form.get("next"))

        # Simple rate limiting
        attempts = session.get("login_attempts", 0)
        last_attempt = session.get("last_attempt", 0)
        now = datetime.now().timestamp()
        if now - last_attempt < 300:  # 5 minutes
            if attempts >= 5:
                logger.warning(f"Rate limit exceeded for login attempts")
                flash("Too many failed attempts. Try again later.", "danger")
                return render_template("login.html", next_url=next_url, csrf_token=generate_csrf())

        if username == admin_username() and check_password_hash(admin_password_hash(), password):
            session["admin_logged_in"] = True
            session["admin_username"] = username
            session.pop("login_attempts", None)
            session.pop("last_attempt", None)
            logger.info(f"Admin login successful: {username}")
            flash("Welcome to the admin dashboard.", "success")
            return redirect(next_url)

        session["login_attempts"] = attempts + 1
        session["last_attempt"] = now
        logger.warning(f"Failed login attempt: {username}")
        flash("Invalid username or password.", "danger")

    return render_template("login.html", next_url=next_url, csrf_token=generate_csrf())


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    username = session.get("admin_username")
    session.clear()
    logger.info(f"Admin logout: {username}")
    flash("You have been logged out.", "info")
    return redirect(url_for("home"))


@app.route("/students")
@login_required
def view_students():
    search = request.args.get("search", "").strip()
    class_filter = request.args.get("class_filter", "").strip()
    section_filter = request.args.get("section_filter", "").strip().upper()

    query = Student.query

    if search:
        wildcard = f"%{search}%"
        query = query.filter(
            or_(
                Student.student_id.ilike(wildcard),
                Student.student_name.ilike(wildcard),
                Student.father_name.ilike(wildcard),
                Student.mother_name.ilike(wildcard),
                Student.mobile_number.ilike(wildcard),
            )
        )

    if class_filter:
        query = query.filter(Student.student_class == class_filter)

    if section_filter:
        query = query.filter(Student.section == section_filter)

    students = (
        query.order_by(
            Student.student_class.asc(),
            Student.section.asc(),
            Student.student_name.asc(),
        ).all()
    )
    class_summary = (
        db.session.query(Student.student_class, func.count(Student.id))
        .group_by(Student.student_class)
        .order_by(Student.student_class.asc())
        .all()
    )
    available_sections = [
        row[0]
        for row in db.session.query(Student.section)
        .distinct()
        .order_by(Student.section.asc())
        .all()
    ]

    return render_template(
        "students.html",
        students=students,
        search=search,
        class_filter=class_filter,
        section_filter=section_filter,
        class_summary=class_summary,
        class_totals={class_name: total for class_name, total in class_summary},
        available_sections=available_sections,
    )


@app.route("/student-registration", methods=["GET", "POST"])
def student_registration():
    submitted_values = {}
    preset_class = request.args.get("class_name", "").strip()
    form_alert = None

    if request.method == "GET":
        clear_public_student_edit()

    if request.method == "POST":
        cleaned_data, errors = validate_student_form(request.form)
        submitted_values = request.form.to_dict()

        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            duplicate_student = find_duplicate_student(cleaned_data)
            if duplicate_student:
                form_alert = {
                    "category": "warning",
                    "message": duplicate_student_message(duplicate_student),
                }
            else:
                student = Student(
                    student_id=generate_student_identifier(),
                    submission_source="student",
                    **student_form_payload(cleaned_data),
                )
                db.session.add(student)
                db.session.commit()
                flash(
                    f"Registration submitted successfully. Your student ID is {student.student_id}.",
                    "success",
                )
                return redirect(
                    url_for("student_registration", class_name=student.student_class)
                )

    if preset_class and "student_class" not in submitted_values:
        submitted_values["student_class"] = preset_class

    return render_template(
        "student_form.html",
        page_title="Student Registration",
        form_mode="public",
        student=None,
        form_values=submitted_values,
        lookup_values={},
        form_alert=form_alert,
        today_iso=date.today().isoformat(),
    )


@app.route("/student-registration/edit", methods=["GET", "POST"])
def student_registration_lookup():
    lookup_values = {}
    form_alert = None

    if request.method == "GET":
        clear_public_student_edit()

    if request.method == "POST":
        lookup_values, errors = validate_public_edit_lookup(request.form)

        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            student = Student.query.filter_by(
                student_id=lookup_values["student_id"],
                mobile_number=lookup_values["mobile_number"],
            ).first()

            if not student:
                clear_public_student_edit()
                flash(
                    "We could not verify a student record with the provided details. "
                    "Please check the student ID and mobile number and try again.",
                    "danger",
                )
            else:
                authorize_public_student_edit(student.student_id)
                flash(
                    f"Record found for {student.student_name}. You can update the student form now.",
                    "success",
                )
                return redirect(
                    url_for("student_registration_edit", student_id=student.student_id)
                )

    return render_template(
        "student_form.html",
        page_title="Find Existing Registration",
        form_mode="public_lookup",
        student=None,
        form_values={},
        lookup_values=lookup_values,
        form_alert=form_alert,
        today_iso=date.today().isoformat(),
    )


@app.route("/student-registration/edit/<student_id>", methods=["GET", "POST"])
def student_registration_edit(student_id):
    normalized_student_id = normalize_student_identifier(student_id)
    form_alert = None

    if not public_student_edit_is_authorized(normalized_student_id):
        flash(
            "Please verify your student ID and mobile number before editing a record.",
            "warning",
        )
        return redirect(url_for("student_registration_lookup"))

    student = Student.query.filter_by(student_id=normalized_student_id).first()
    if not student:
        clear_public_student_edit()
        flash("This student record is no longer available.", "danger")
        return redirect(url_for("student_registration_lookup"))

    submitted_values = {}

    if request.method == "POST":
        cleaned_data, errors = validate_student_form(request.form)
        submitted_values = request.form.to_dict()

        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            duplicate_student = find_duplicate_student(
                cleaned_data, exclude_student_pk=student.id
            )
            if duplicate_student:
                form_alert = {
                    "category": "warning",
                    "message": duplicate_student_message(duplicate_student),
                }
            else:
                apply_student_form_data(student, cleaned_data)
                db.session.commit()
                flash(
                    f"Registration updated successfully for student ID {student.student_id}.",
                    "success",
                )
                return redirect(
                    url_for("student_registration_edit", student_id=student.student_id)
                )

    return render_template(
        "student_form.html",
        page_title="Update Existing Registration",
        form_mode="public_edit",
        student=student,
        form_values=submitted_values,
        lookup_values={},
        form_alert=form_alert,
        today_iso=date.today().isoformat(),
    )


@app.route("/students/add", methods=["GET", "POST"])
@login_required
def add_student():
    submitted_values = {}
    form_alert = None

    if request.method == "POST":
        cleaned_data, errors = validate_student_form(request.form)
        submitted_values = request.form.to_dict()

        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            duplicate_student = find_duplicate_student(cleaned_data)
            if duplicate_student:
                form_alert = {
                    "category": "warning",
                    "message": duplicate_student_message(duplicate_student),
                }
            else:
                student = Student(
                    student_id=generate_student_identifier(),
                    submission_source="admin",
                    **student_form_payload(cleaned_data),
                )
                db.session.add(student)
                db.session.commit()
                flash(
                    f"Student saved successfully with ID {student.student_id}.",
                    "success",
                )
                return redirect(url_for("view_students"))

    return render_template(
        "student_form.html",
        page_title="Add Student",
        form_mode="add",
        student=None,
        form_values=submitted_values,
        lookup_values={},
        form_alert=form_alert,
        today_iso=date.today().isoformat(),
    )


@app.route("/students/class/<class_name>")
@login_required
def class_view(class_name):
    return redirect(url_for("view_students", class_filter=class_name))


@app.route("/students/<int:student_pk>")
@login_required
def student_detail(student_pk):
    student = Student.query.get_or_404(student_pk)
    return render_template("student_detail.html", student=student)


@app.route("/students/<int:student_pk>/edit", methods=["GET", "POST"])
@login_required
def edit_student(student_pk):
    student = Student.query.get_or_404(student_pk)
    submitted_values = {}
    form_alert = None

    if request.method == "POST":
        cleaned_data, errors = validate_student_form(request.form)
        submitted_values = request.form.to_dict()

        if errors:
            for error in errors:
                flash(error, "danger")
        else:
            duplicate_student = find_duplicate_student(
                cleaned_data, exclude_student_pk=student.id
            )
            if duplicate_student:
                form_alert = {
                    "category": "warning",
                    "message": duplicate_student_message(duplicate_student),
                }
            else:
                apply_student_form_data(student, cleaned_data)
                db.session.commit()
                flash(f"Student {student.student_id} updated successfully.", "success")
                return redirect(url_for("view_students"))

    return render_template(
        "student_form.html",
        page_title="Edit Student",
        form_mode="edit",
        student=student,
        form_values=submitted_values,
        lookup_values={},
        form_alert=form_alert,
        today_iso=date.today().isoformat(),
    )


@app.route("/students/<int:student_pk>/delete", methods=["POST"])
@login_required
def delete_student(student_pk):
    student = Student.query.get_or_404(student_pk)
    deleted_student_id = student.student_id
    db.session.delete(student)
    db.session.commit()
    flash(f"Student {deleted_student_id} has been deleted.", "info")
    return redirect(url_for("view_students"))


@app.route("/students/<int:student_pk>/print")
@login_required
def print_student(student_pk):
    student = Student.query.get_or_404(student_pk)
    return render_template("student_print.html", student=student)


@app.route("/students/export")
@login_required
def export_students():
    export_class = request.args.get("class_name", "").strip()

    students_query = Student.query
    if export_class:
        students_query = students_query.filter(Student.student_class == export_class)

    students = (
        students_query.order_by(
            Student.student_class.asc(),
            Student.section.asc(),
            Student.student_name.asc(),
        ).all()
    )

    workbook = Workbook()
    worksheet = workbook.active
    worksheet.title = (
        f"Class {export_class}"[:31] if export_class else "Students"
    )

    headers = [
        "Student ID",
        "Student Name",
        "Father's Name",
        "Mother's Name",
        "Date of Birth",
        "Gender",
        "Class",
        "Section",
        "Mobile Number",
        "Address",
        "Submission Source",
        "Created At",
    ]
    worksheet.append(headers)

    for student in students:
        worksheet.append(
            [
                student.student_id,
                student.student_name,
                student.father_name,
                student.mother_name,
                student.date_of_birth.strftime("%d-%m-%Y"),
                student.gender,
                student.student_class,
                student.section,
                student.mobile_number,
                student.address,
                student.submission_source.title(),
                student.created_at.strftime("%d-%m-%Y %I:%M %p"),
            ]
        )

    for column in worksheet.columns:
        max_length = 0
        column_letter = column[0].column_letter
        for cell in column:
            value = str(cell.value) if cell.value is not None else ""
            max_length = max(max_length, len(value))
        worksheet.column_dimensions[column_letter].width = min(max_length + 4, 35)

    output = io.BytesIO()
    workbook.save(output)
    output.seek(0)

    if export_class:
        safe_class = re.sub(r"[^A-Za-z0-9_-]+", "-", export_class)
        filename = (
            f"indian_public_school_class_{safe_class}_{date.today().isoformat()}.xlsx"
        )
    else:
        filename = f"indian_public_school_students_{date.today().isoformat()}.xlsx"

    return send_file(
        output,
        as_attachment=True,
        download_name=filename,
        mimetype=(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
    )


@app.errorhandler(404)
def not_found(_error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    logger.error(f"Internal server error: {error}")
    return "Internal Server Error", 500


with app.app_context():
    db.create_all()


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)