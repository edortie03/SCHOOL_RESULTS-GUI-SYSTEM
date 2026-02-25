"""
services/auth_service.py - Authentication and authorization service
"""
import bcrypt
import logging
from sqlalchemy.orm import Session
from models.user import Admin, Teacher
from models.student import Student

logger = logging.getLogger(__name__)


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def hash_password(plain: str) -> str:
        return bcrypt.hashpw(plain.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    @staticmethod
    def verify_password(plain: str, hashed: str) -> bool:
        try:
            return bcrypt.checkpw(plain.encode("utf-8"), hashed.encode("utf-8"))
        except Exception:
            return False

    def login(self, email: str, password: str, admission_number: str = None):
        """Return (user_object, role) or (None, None).
        
        Args:
            email: Email address for admin/teacher login
            password: Password for authentication
            admission_number: Admission number for student login (optional, uses email if not provided)
        """
        # Ensure clean session state
        try:
            self.db.rollback()
        except:
            pass
        
        # Try student login first if admission_number is provided
        if admission_number:
            try:
                student = self.db.query(Student).filter(Student.admission_number == admission_number).first()
                if student and student.password_hash and self.verify_password(password, student.password_hash):
                    logger.info(f"Student login: {admission_number}")
                    return student, "STUDENT"
            except Exception as e:
                logger.error(f"Error querying student: {e}")
                self.db.rollback()

        # Otherwise try email-based login (admin/teacher)
        email = email.strip().lower() if email else ""

        try:
            admin = self.db.query(Admin).filter(Admin.email == email).first()
            if admin and self.verify_password(password, admin.password_hash):
                logger.info(f"Admin login: {email}")
                return admin, "ADMIN"
        except Exception as e:
            logger.error(f"Error querying admin: {e}")
            self.db.rollback()

        try:
            teacher = self.db.query(Teacher).filter(Teacher.email == email).first()
            if teacher and self.verify_password(password, teacher.password_hash):
                logger.info(f"Teacher login: {email}")
                return teacher, "TEACHER"
        except Exception as e:
            logger.error(f"Error querying teacher: {e}")
            self.db.rollback()

        logger.warning(f"Failed login attempt for: {email}")
        return None, None

    def create_admin(self, full_name: str, email: str, password: str) -> Admin:
        email = email.strip().lower()
        if self.db.query(Admin).filter(Admin.email == email).first():
            raise ValueError("Admin with this email already exists.")
        admin = Admin(
            full_name=full_name,
            email=email,
            password_hash=self.hash_password(password),
        )
        try:
            self.db.add(admin)
            self.db.commit()
            self.db.refresh(admin)
            return admin
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating admin: {e}")
            raise

    def seed_default_admin(self):
        """Create default admin if none exists."""
        if not self.db.query(Admin).first():
            self.create_admin("System Administrator", "admin@school.edu", "Admin@1234")
            logger.info("Default admin seeded: admin@school.edu / Admin@1234")

    def create_teacher(self, full_name: str, email: str, password: str) -> Teacher:
        """Register a new teacher."""
        email = email.strip().lower()
        if self.db.query(Teacher).filter(Teacher.email == email).first():
            raise ValueError("A teacher with this email already exists.")
        if self.db.query(Admin).filter(Admin.email == email).first():
            raise ValueError("An admin with this email already exists.")
        teacher = Teacher(
            full_name=full_name.strip(),
            email=email,
            password_hash=self.hash_password(password),
        )
        try:
            self.db.add(teacher)
            self.db.commit()
            self.db.refresh(teacher)
            logger.info(f"Teacher registered: {teacher.full_name}")
            return teacher
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating teacher: {e}")
            raise
