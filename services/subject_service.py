"""
services/subject_service.py - Subject CRUD service
"""
import logging
from sqlalchemy.orm import Session
from models.subject import Subject

logger = logging.getLogger(__name__)


class SubjectService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        # Ensure session is fresh before query
        try:
            self.db.rollback()
        except:
            pass
        return self.db.query(Subject).order_by(Subject.subject_name).all()

    def get_by_id(self, subject_id: int):
        return self.db.query(Subject).filter(Subject.id == subject_id).first()

    def get_by_class(self, class_id: int):
        return self.db.query(Subject).filter(Subject.class_id == class_id).all()

    def get_by_teacher(self, teacher_id: int):
        return self.db.query(Subject).filter(Subject.teacher_id == teacher_id).all()

    def create(self, subject_name: str, class_id: int = None, teacher_id: int = None) -> Subject:
        subject = Subject(
            subject_name=subject_name.strip(),
            class_id=class_id,
            teacher_id=teacher_id,
        )
        try:
            self.db.add(subject)
            self.db.commit()
            self.db.refresh(subject)
            logger.info(f"Subject created: {subject.subject_name}")
            return subject
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating subject: {e}")
            raise

    def update(self, subject_id: int, subject_name: str, class_id: int = None, teacher_id: int = None) -> Subject:
        subject = self.get_by_id(subject_id)
        if not subject:
            raise ValueError("Subject not found.")
        subject.subject_name = subject_name.strip()
        subject.class_id = class_id
        subject.teacher_id = teacher_id
        try:
            self.db.commit()
            self.db.refresh(subject)
            return subject
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating subject: {e}")
            raise

    def delete(self, subject_id: int):
        subject = self.get_by_id(subject_id)
        if not subject:
            raise ValueError("Subject not found.")
        try:
            self.db.delete(subject)
            self.db.commit()
            logger.info(f"Subject deleted id={subject_id}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting subject: {e}")
            raise
