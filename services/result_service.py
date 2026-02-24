"""
services/result_service.py - Result CRUD service
"""
import logging
from sqlalchemy.orm import Session
from models.result import Result

logger = logging.getLogger(__name__)


class ResultService:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self):
        return self.db.query(Result).all()

    def get_by_id(self, result_id: int):
        return self.db.query(Result).filter(Result.id == result_id).first()

    def get_by_student(self, student_id: int):
        return self.db.query(Result).filter(Result.student_id == student_id).all()

    def get_by_subject(self, subject_id: int):
        return self.db.query(Result).filter(Result.subject_id == subject_id).all()

    def exists(self, student_id: int, subject_id: int):
        return self.db.query(Result).filter(
            Result.student_id == student_id,
            Result.subject_id == subject_id,
        ).first()

    def add_result(self, student_id: int, subject_id: int, marks: float) -> Result:
        if marks < 0 or marks > 100:
            raise ValueError("Marks must be between 0 and 100.")
        if self.exists(student_id, subject_id):
            raise ValueError("Result for this student and subject already exists. Use update instead.")
        grade, gpa, remarks = Result.calculate_grade_gpa(marks)
        result = Result(
            student_id=student_id,
            subject_id=subject_id,
            marks=marks,
            grade=grade,
            gpa=gpa,
            remarks=remarks,
        )
        try:
            self.db.add(result)
            self.db.commit()
            self.db.refresh(result)
            logger.info(f"Result added: student={student_id} subject={subject_id} marks={marks} grade={grade}")
            return result
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error adding result: {e}")
            raise

    def update_result(self, result_id: int, marks: float) -> Result:
        if marks < 0 or marks > 100:
            raise ValueError("Marks must be between 0 and 100.")
        result = self.get_by_id(result_id)
        if not result:
            raise ValueError("Result not found.")
        grade, gpa, remarks = Result.calculate_grade_gpa(marks)
        result.marks = marks
        result.grade = grade
        result.gpa = gpa
        result.remarks = remarks
        try:
            self.db.commit()
            self.db.refresh(result)
            return result
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating result: {e}")
            raise

    def delete_result(self, result_id: int):
        result = self.get_by_id(result_id)
        if not result:
            raise ValueError("Result not found.")
        try:
            self.db.delete(result)
            self.db.commit()
            logger.info(f"Result deleted id={result_id}")
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting result: {e}")
            raise

    def get_class_results(self, class_id: int):
        """Get all results for students in a class."""
        from models.student import Student
        return (
            self.db.query(Result)
            .join(Student, Result.student_id == Student.id)
            .filter(Student.class_id == class_id)
            .all()
        )
