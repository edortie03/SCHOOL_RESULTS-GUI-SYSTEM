"""
services/analytics_service.py - Analytics data computation
"""
import logging
from sqlalchemy.orm import Session
from sqlalchemy import func
from models.result import Result
from models.student import Student
from models.subject import Subject
from models.class_model import Class

logger = logging.getLogger(__name__)


class AnalyticsService:
    def __init__(self, db: Session):
        self.db = db

    def class_average(self):
        """Return list of (class_name, avg_marks)."""
        rows = (
            self.db.query(Class.class_name, func.avg(Result.marks).label("avg"))
            .join(Student, Student.class_id == Class.id)
            .join(Result, Result.student_id == Student.id)
            .group_by(Class.class_name)
            .all()
        )
        return [(r.class_name, round(r.avg, 2)) for r in rows]

    def subject_average(self):
        """Return list of (subject_name, avg_marks)."""
        rows = (
            self.db.query(Subject.subject_name, func.avg(Result.marks).label("avg"))
            .join(Result, Result.subject_id == Subject.id)
            .group_by(Subject.subject_name)
            .all()
        )
        return [(r.subject_name, round(r.avg, 2)) for r in rows]

    def top_students(self, limit: int = 5):
        """Return list of (student_name, avg_marks) top performers."""
        rows = (
            self.db.query(
                Student.first_name,
                Student.last_name,
                func.avg(Result.marks).label("avg"),
            )
            .join(Result, Result.student_id == Student.id)
            .group_by(Student.id, Student.first_name, Student.last_name)
            .order_by(func.avg(Result.marks).desc())
            .limit(limit)
            .all()
        )
        return [(f"{r.first_name} {r.last_name}", round(r.avg, 2)) for r in rows]

    def pass_fail_rate(self):
        """Return (pass_count, fail_count)."""
        total = self.db.query(Result).count()
        pass_count = self.db.query(Result).filter(Result.marks >= 50).count()
        fail_count = total - pass_count
        return pass_count, fail_count

    def gpa_distribution(self):
        """Return dict of grade -> count."""
        rows = (
            self.db.query(Result.grade, func.count(Result.id).label("cnt"))
            .group_by(Result.grade)
            .all()
        )
        return {r.grade: r.cnt for r in rows}

    def total_stats(self):
        """Return dict with overall stats."""
        # Ensure session is fresh before query
        try:
            self.db.rollback()
        except:
            pass
        total_students = self.db.query(Student).count()
        total_results = self.db.query(Result).count()
        avg_marks = self.db.query(func.avg(Result.marks)).scalar() or 0
        return {
            "total_students": total_students,
            "total_results": total_results,
            "avg_marks": round(avg_marks, 2),
        }
