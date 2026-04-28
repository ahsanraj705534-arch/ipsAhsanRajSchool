from pathlib import Path
from datetime import date
from jinja2 import Template

root = Path(r"d:\coding\indian_Public_School")
template_path = root / "templates" / "student_print.html"
out_path = root / "student_print_preview.html"

template_text = template_path.read_text(encoding="utf-8")

def url_for(endpoint, **values):
    if endpoint == "static":
        return "static/" + values["filename"].replace("\\", "/")
    if endpoint == "student_detail":
        return "#"
    return "#"

class Obj:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

student = Obj(
    id=1,
    student_name="Mohd Zishan",
    student_id="IPS20260003",
    student_class="7",
    section="F",
    submission_source="student",
    gender="Male",
    date_of_birth=date(2015, 1, 2),
    father_name="Abdul Rahman",
    mother_name="Sajo",
    mobile_number="8278965370",
    address="Rasulpur Dabheri",
    photo_url="static/images/students-outdoor-study.jpg",
)
school_info = Obj(
    name="Indian Public School",
    address="Rasulpur Dabheri, Budhana, Muzaffarnagar, Uttar Pradesh, India",
)
html = Template(template_text).render(student=student, school_info=school_info, url_for=url_for)
out_path.write_text(html, encoding="utf-8")
print(out_path)
