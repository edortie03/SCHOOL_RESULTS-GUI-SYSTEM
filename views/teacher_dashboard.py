"""
views/teacher_dashboard.py - Teacher dashboard (restricted view)
"""
import tkinter as tk
from config import COLORS, FONTS
from views.base_dashboard import BaseDashboard
from views.results_panel import ResultsPanel
from services import StudentService, SubjectService, ResultService, ClassService
from config import SessionLocal


class TeacherDashboard(BaseDashboard):
    def __init__(self, master, user, logout_callback):
        self._user = user
        self._logout_callback = logout_callback
        self._init_services(user)
        self.NAV_ITEMS = [
            ("My Subjects & Marks", self._show_results),
            ("My Class Performance", self._show_class_perf),
        ]
        super().__init__(master, user, "TEACHER", logout_callback)
        self._nav_click("My Subjects & Marks", self._show_results)

    def _init_services(self, user):
        # Create separate session for each service to prevent transaction issues
        self.student_svc = StudentService(SessionLocal())
        self.subject_svc = SubjectService(SessionLocal())
        self.result_svc = ResultService(SessionLocal())
        self.class_svc = ClassService(SessionLocal())

    def _show_results(self):
        self.update_section_title("Enter Student Marks")
        ResultsPanel(
            self.get_content_frame(),
            self.result_svc, self.student_svc, self.subject_svc, self.class_svc,
            teacher=self.user,
        )

    def _show_class_perf(self):
        self.update_section_title("Class Performance")
        f = self.get_content_frame()
        subjects = self.subject_svc.get_by_teacher(self.user.id)

        tk.Label(f, text="Subjects Assigned to You",
                 font=FONTS["subheading"], bg=COLORS["bg_medium"],
                 fg=COLORS["text_primary"]).pack(anchor="w", padx=20, pady=(14, 6))

        if not subjects:
            tk.Label(f, text="No subjects assigned.",
                     font=FONTS["body"], bg=COLORS["bg_medium"],
                     fg=COLORS["text_secondary"]).pack(padx=20)
            return

        for subject in subjects:
            card = tk.Frame(f, bg=COLORS["card"], padx=16, pady=12,
                            highlightbackground=COLORS["border"], highlightthickness=1)
            card.pack(fill="x", padx=20, pady=6)
            tk.Label(card, text=subject.subject_name, font=FONTS["body_bold"],
                     bg=COLORS["card"], fg=COLORS["text_primary"]).pack(anchor="w")
            class_name = subject.class_.class_name if subject.class_ else "—"
            tk.Label(card, text=f"Class: {class_name}",
                     font=FONTS["small"], bg=COLORS["card"],
                     fg=COLORS["text_secondary"]).pack(anchor="w")

            results = self.result_svc.get_by_subject(subject.id)
            if results:
                avg = sum(r.marks for r in results) / len(results)
                pass_c = sum(1 for r in results if r.marks >= 50)
                tk.Label(card,
                         text=f"Students: {len(results)}  |  Avg: {avg:.1f}  |  Pass: {pass_c}/{len(results)}",
                         font=FONTS["small"], bg=COLORS["card"],
                         fg=COLORS["accent"]).pack(anchor="w", pady=(4, 0))
            else:
                tk.Label(card, text="No marks entered yet.",
                         font=FONTS["small"], bg=COLORS["card"],
                         fg=COLORS["text_secondary"]).pack(anchor="w")
