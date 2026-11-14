"""Insert demo users/spaces after `alembic upgrade head`.

One password is chosen interactively and assigned to all demo accounts.
"""
from getpass import getpass
import bcrypt
from sqlalchemy import create_engine, text
from app.config import settings

if not settings.database_url:
    raise SystemExit("DATABASE_URL is missing. Configure backend/.env first.")

password = getpass("Choose one password for all local demo accounts: ").encode("utf-8")
if not 1 <= len(password) <= 72:
    raise SystemExit("Enter a password between 1 and 72 bytes.")
password_hash = bcrypt.hashpw(password, bcrypt.gensalt(rounds=settings.bcrypt_rounds)).decode("utf-8")
engine = create_engine(settings.database_url, pool_pre_ping=True)

users = [
    ("Demo Student", "demo.student.90001@khi.iba.edu.pk", "student", "enrolled", "90001", "EN-90001", "BSCS", False, None, ""),
    ("Demo TA", "demo.ta.90002@khi.iba.edu.pk", "ta", "enrolled", "90002", "EN-90002", "MSCS", True, None, "SOCIETY,OSA"),
    ("Demo Alumni", "demo.alumni.90003@khi.iba.edu.pk", "student", "alumni", "90003", "EN-90003", "BSCS", False, None, ""),
    ("Demo Faculty", "faculty.demo@iba.edu.pk", "faculty", None, None, None, None, False, "Computer Science", ""),
    ("Demo Admin", "admin.demo@iba.edu.pk", "admin", None, None, None, None, False, None, ""),
]

spaces = [
    ("Demo Study Room", "Library Level 1", 8),
    ("Demo Seminar Room", "Academic Block", 30),
    ("Demo Computing Lab", "Lab Block", 24),
]

with engine.begin() as connection:
    for row in users:
        (name, email, role, status, erp_id, enrollment_number, program,
         is_ta, department, represents) = row
        connection.execute(text("""
            INSERT INTO public.users
                (name, email, role, student_status, password_hash, erp_id,
                 enrollment_number, program, is_ta, department, represents, is_active)
            VALUES
                (:name, :email, :role, :status, :password_hash, :erp_id,
                 :enrollment_number, :program, :is_ta, :department, :represents, TRUE)
            ON CONFLICT (email) DO UPDATE SET
                name = EXCLUDED.name,
                role = EXCLUDED.role,
                student_status = EXCLUDED.student_status,
                password_hash = EXCLUDED.password_hash,
                erp_id = EXCLUDED.erp_id,
                enrollment_number = EXCLUDED.enrollment_number,
                program = EXCLUDED.program,
                is_ta = EXCLUDED.is_ta,
                department = EXCLUDED.department,
                represents = EXCLUDED.represents,
                is_active = TRUE
        """), {
            "name": name, "email": email, "role": role, "status": status,
            "password_hash": password_hash, "erp_id": erp_id,
            "enrollment_number": enrollment_number, "program": program,
            "is_ta": is_ta, "department": department, "represents": represents,
        })

    for name, location, capacity in spaces:
        connection.execute(text("""
            INSERT INTO public.spaces (name, location, capacity)
            VALUES (:name, :location, :capacity)
            ON CONFLICT (name, location) DO NOTHING
        """), {"name": name, "location": location, "capacity": capacity})

print("Demo users and spaces inserted/updated.")
print("Student: demo.student.90001@khi.iba.edu.pk | ERP 90001 | Enrollment EN-90001")
print("TA: demo.ta.90002@khi.iba.edu.pk | ERP 90002 | Enrollment EN-90002")
print("Faculty: faculty.demo@iba.edu.pk")
print("Admin: admin.demo@iba.edu.pk")
print("Use the password you just entered for all accounts.")
