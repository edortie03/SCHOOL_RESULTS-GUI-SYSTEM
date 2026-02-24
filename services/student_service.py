"""
services/student_service.py - Student CRUD service with search and pagination
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import or_
from models.student import Student

logger = logging.getLogger(__name__)


class StudentService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Student).order_by(Student.first_name).all()

    def get_by_id(self, student_id: int):
        return self.db.query(Student).filter(Student.id == student_id).first()

    def get_by_admission(self, admission_number: str):
        return self.db.query(Student).filter(Student.admission_number == admission_number).first()

    def get_by_class(self, class_id: int):
        return self.db.query(Student).filter(Student.class_id == class_id).all()

    def search(self, query: str, class_id: int = None, page: int = 1, page_size: int = 20):
        """Search students with optional class filter and pagination."""
        q = self.db.query(Student)
        if query:
            pattern = f"%{query}%"
            q = q.filter(
                or_(
                    Student.first_name.ilike(pattern),
                    Student.last_name.ilike(pattern),
                    Student.admission_number.ilike(pattern),
                )
            )
        if class_id:
            q = q.filter(Student.class_id == class_id)
        total = q.count()
        students = q.order_by(Student.first_name).offset((page - 1) * page_size).limit(page_size).all()
        return students, total

    def create(self, admission_number: str, first_name: str, last_name: str,
               gender: str, date_of_birth=None, class_id: int = None, password_hash: str = None) -> Student:
        if self.get_by_admission(admission_number):
            raise ValueError(f"Student with admission number '{admission_number}' already exists.")
        student = Student(
            admission_number=admission_number.strip(),
            first_name=first_name.strip(),
            last_name=last_name.strip(),
            gender=gender,
            date_of_birth=date_of_birth,
            class_id=class_id,
            password_hash=password_hash,
        )
        try:
            self.db.add(student)
            self.db.commit()
            self.db.refresh(student)
            logger.info(f"Student created: {student.full_name} ({student.admission_number})")
            return student
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating student: {e}")
            raise

    def update(self, student_id: int, admission_number: str, first_name: str, last_name: str,
               gender: str, date_of_birth=None, class_id: int = None) -> Student:
        student = self.get_by_id(student_id)
        if not student:
            raise ValueError("Student not found.")
        existing = self.get_by_admission(admission_number)
        if existing and existing.id != student_id:
            raise ValueError("Admission number already in use.")
        student.admission_number = admission_number.strip()
        student.first_name = first_name.strip()
        student.last_name = last_name.strip()
        student.gender = gender
        student.date_of_birth = date_of_birth
        student.class_id = class_id
        try:
            self.db.commit()
            self.db.refresh(student)
            return student
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating student: {e}")
            raise

    def delete(self, student_id: int):
        student = self.get_by_id(student_id)
        if not student:
            raise ValueError("Student not found.")
        try:
            self.db.delete(student)
            self.db.commit()
            logger.info(f"Student deleted id={student_id}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting student: {e}")
            raise
