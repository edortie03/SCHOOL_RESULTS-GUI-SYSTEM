"""
services/class_service.py - Class CRUD service
"""
import logging
from sqlalchemy.orm import Session
from models.class_model import Class

logger = logging.getLogger(__name__)


class ClassService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Class).order_by(Class.class_name).all()

    def get_by_id(self, class_id: int):
        return self.db.query(Class).filter(Class.id == class_id).first()

    def create(self, class_name: str, academic_year: str) -> Class:
        cls = Class(class_name=class_name.strip(), academic_year=academic_year.strip())
        try:
            self.db.add(cls)
            self.db.commit()
            self.db.refresh(cls)
            logger.info(f"Class created: {cls.class_name}")
            return cls
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating class: {e}")
            raise

    def update(self, class_id: int, class_name: str, academic_year: str) -> Class:
        cls = self.get_by_id(class_id)
        if not cls:
            raise ValueError("Class not found.")
        cls.class_name = class_name.strip()
        cls.academic_year = academic_year.strip()
        try:
            self.db.commit()
            self.db.refresh(cls)
            return cls
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating class: {e}")
            raise

    def delete(self, class_id: int):
        cls = self.get_by_id(class_id)
        if not cls:
            raise ValueError("Class not found.")
        try:
            self.db.delete(cls)
            self.db.commit()
            logger.info(f"Class deleted id={class_id}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting class: {e}")
            raise
