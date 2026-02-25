"""
views/admin_dashboard.py - Full admin dashboard
"""
import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS
from views.base_dashboard import BaseDashboard
from views.students_panel import StudentsPanel
from views.teachers_panel import TeachersPanel
from views.classes_subjects_panel import ClassesSubjectsPanel
from views.results_panel import ResultsPanel
from views.analytics_panel import AnalyticsPanel
from views.reports_panel import ReportsPanel
from services import (
    StudentService, TeacherService, ClassService,
    SubjectService, ResultService, ReportService, AnalyticsService
)
from config import SessionLocal


class AdminDashboard(BaseDashboard):
    def __init__(self, master, user, logout_callback):
        self._user = user
        self._logout_callback = logout_callback
        self._init_services()
        self.NAV_ITEMS = [
            ("Dashboard",   self._show_overview),
            ("Students",    self._show_students),
            ("Teachers",    self._show_teachers),
            ("Classes & Subjects", self._show_classes),
            ("Results",     self._show_results),
            ("Analytics",   self._show_analytics),
            ("Reports",     self._show_reports),
        ]
        super().__init__(master, user, "ADMIN", logout_callback)
        # Auto-load overview
        self._nav_click("Dashboard", self._show_overview)

    def _init_services(self):
        # Create separate session for each service to prevent transaction issues
        self.student_svc = StudentService(SessionLocal())
        self.teacher_svc = TeacherService(SessionLocal())
        self.class_svc = ClassService(SessionLocal())
        self.subject_svc = SubjectService(SessionLocal())
        self.result_svc = ResultService(SessionLocal())
        self.report_svc = ReportService(SessionLocal())
        self.analytics_svc = AnalyticsService(SessionLocal())

    def _show_overview(self):
        self.update_section_title("Dashboard Overview")
        f = self.get_content_frame()
        stats = self.analytics_svc.total_stats()
        header = tk.Frame(f, bg=COLORS["bg_medium"], pady=16)
        header.pack(fill="x", padx=20)
        tk.Label(header, text=f"Welcome, {self.user.full_name}",
                 font=FONTS["heading"], bg=COLORS["bg_medium"],
                 fg=COLORS["white"]).pack(anchor="w")
        tk.Label(header, text="School Examination Results Management System",
                 font=FONTS["body"], bg=COLORS["bg_medium"],
                 fg=COLORS["text_secondary"]).pack(anchor="w")

        cards_row = tk.Frame(f, bg=COLORS["bg_medium"])
        cards_row.pack(fill="x", padx=20, pady=12)
        stat_items = [
            ("Total Students", stats["total_students"], COLORS["primary"]),
            ("Total Results",  stats["total_results"],  COLORS["secondary"]),
            ("Average Score",  f"{stats['avg_marks']}%", COLORS["success"]),
        ]
        for i, (label, val, color) in enumerate(stat_items):
            card = tk.Frame(cards_row, bg=color, padx=28, pady=22)
            card.grid(row=0, column=i, padx=10, sticky="ew")
            cards_row.columnconfigure(i, weight=1)
            tk.Label(card, text=str(val), font=("Segoe UI", 32, "bold"),
                     bg=color, fg="white").pack()
            tk.Label(card, text=label, font=FONTS["body"],
                     bg=color, fg="#d0d8ff").pack()

        # Quick nav
        quick = tk.Frame(f, bg=COLORS["bg_medium"])
        quick.pack(fill="x", padx=20, pady=8)
        tk.Label(quick, text="Quick Actions", font=FONTS["subheading"],
                 bg=COLORS["bg_medium"], fg=COLORS["text_primary"]).pack(anchor="w", pady=(0, 8))

        btn_row = tk.Frame(quick, bg=COLORS["bg_medium"])
        btn_row.pack(fill="x")
        for i, (text, section, callback) in enumerate([
            ("Manage Students",  "Students",          self._show_students),
            ("Enter Marks",      "Results",            self._show_results),
            ("View Analytics",   "Analytics",          self._show_analytics),
            ("Generate Reports", "Reports",            self._show_reports),
        ]):
            tk.Button(btn_row, text=text, font=FONTS["body_bold"],
                      bg=COLORS["card"], fg=COLORS["text_primary"],
                      activebackground=COLORS["hover"], relief="flat",
                      cursor="hand2", padx=20, pady=16,
                      command=lambda s=section, cb=callback: self._nav_click(s, cb),
                      highlightbackground=COLORS["border"], highlightthickness=1,
                      ).grid(row=0, column=i, padx=6, sticky="ew")
            btn_row.columnconfigure(i, weight=1)

    def _show_students(self):
        self.update_section_title("Student Management")
        StudentsPanel(self.get_content_frame(), self.student_svc, self.class_svc)

    def _show_teachers(self):
        self.update_section_title("Teacher Management")
        TeachersPanel(self.get_content_frame(), self.teacher_svc, self.subject_svc)

    def _show_classes(self):
        self.update_section_title("Classes & Subjects")
        ClassesSubjectsPanel(self.get_content_frame(), self.class_svc,
                             self.subject_svc, self.teacher_svc)

    def _show_results(self):
        self.update_section_title("Results Management")
        ResultsPanel(self.get_content_frame(), self.result_svc,
                     self.student_svc, self.subject_svc, self.class_svc)

    def _show_analytics(self):
        self.update_section_title("Analytics Dashboard")
        AnalyticsPanel(self.get_content_frame(), self.analytics_svc)

    def _show_reports(self):
        self.update_section_title("Report Generation")
        ReportsPanel(self.get_content_frame(), self.report_svc,
                     self.student_svc, self.class_svc)
