"""
services/teacher_service.py - Teacher CRUD service
"""
import logging
from sqlalchemy.orm import Session
from models.user import Teacher
from services.auth_service import AuthService

logger = logging.getLogger(__name__)


class TeacherService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Teacher).order_by(Teacher.full_name).all()

    def get_by_id(self, teacher_id: int):
        return self.db.query(Teacher).filter(Teacher.id == teacher_id).first()

    def get_by_email(self, email: str):
        return self.db.query(Teacher).filter(Teacher.email == email.strip().lower()).first()

    def create(self, full_name: str, email: str, password: str) -> Teacher:
        email = email.strip().lower()
        if self.get_by_email(email):
            raise ValueError("A teacher with this email already exists.")
        teacher = Teacher(
            full_name=full_name.strip(),
            email=email,
            password_hash=AuthService.hash_password(password),
        )
        try:
            self.db.add(teacher)
            self.db.commit()
            self.db.refresh(teacher)
            logger.info(f"Teacher created: {teacher.full_name}")
            return teacher
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating teacher: {e}")
            raise

    def update(self, teacher_id: int, full_name: str, email: str, password: str = None) -> Teacher:
        teacher = self.get_by_id(teacher_id)
        if not teacher:
            raise ValueError("Teacher not found.")
        email = email.strip().lower()
        existing = self.get_by_email(email)
        if existing and existing.id != teacher_id:
            raise ValueError("Email already in use by another teacher.")
        teacher.full_name = full_name.strip()
        teacher.email = email
        if password:
            teacher.password_hash = AuthService.hash_password(password)
        try:
            self.db.commit()
            self.db.refresh(teacher)
            return teacher
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating teacher: {e}")
            raise

    def delete(self, teacher_id: int):
        teacher = self.get_by_id(teacher_id)
        if not teacher:
            raise ValueError("Teacher not found.")
        try:
            self.db.delete(teacher)
            self.db.commit()
            logger.info(f"Teacher deleted id={teacher_id}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting teacher: {e}")
            raise
