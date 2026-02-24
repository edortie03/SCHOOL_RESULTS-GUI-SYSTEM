"""
models/student.py - Student ORM model
"""
from datetime import datetime
from sqlalchemy import Column, Integer, String, Date, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from config import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    admission_number = Column(String(30), unique=True, nullable=False, index=True)
    first_name = Column(String(80), nullable=False)
    last_name = Column(String(80), nullable=False)
    gender = Column(String(10), nullable=False)
    date_of_birth = Column(Date, nullable=True)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=True)
    password_hash = Column(String(255), nullable=True)  # For student login
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    class_ = relationship("Class", back_populates="students")
    results = relationship("Result", back_populates="student", cascade="all, delete-orphan")

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"

    def __repr__(self):
        return f"<Student id={self.id} adm={self.admission_number} name={self.full_name}>"
