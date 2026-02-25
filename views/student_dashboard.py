"""
views/student_dashboard.py - Student dashboard (restricted view)
"""
import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS
from views.base_dashboard import BaseDashboard
from services import ResultService, SubjectService, ClassService
from config import SessionLocal


class StudentDashboard(BaseDashboard):
    def __init__(self, master, user, logout_callback):
        self._user = user
        self._logout_callback = logout_callback
        self._init_services(user)
        self.NAV_ITEMS = [
            ("My Results", self._show_results),
            ("My Profile", self._show_profile),
        ]
        super().__init__(master, user, "STUDENT", logout_callback)
        self._nav_click("My Results", self._show_results)

    def _init_services(self, user):
        # Create separate session for each service to prevent transaction issues
        self.result_svc = ResultService(SessionLocal())
        self.subject_svc = SubjectService(SessionLocal())
        self.class_svc = ClassService(SessionLocal())

    def _show_results(self):
        self.update_section_title("My Results")
        f = self.get_content_frame()
        
        # Get student's results
        results = self.result_svc.get_by_student(self.user.id)
        
        # Header
        header = tk.Frame(f, bg=COLORS["bg_medium"], pady=16)
        header.pack(fill="x", padx=20)
        tk.Label(header, text=f"Welcome, {self.user.full_name}",
                 font=FONTS["heading"], bg=COLORS["bg_medium"],
                 fg=COLORS["white"]).pack(anchor="w")
        tk.Label(header, text=f"Admission Number: {self.user.admission_number}",
                 font=FONTS["body"], bg=COLORS["bg_medium"],
                 fg=COLORS["text_secondary"]).pack(anchor="w")

        if not results:
            tk.Label(f, text="No results available yet.",
                     font=FONTS["body"], bg=COLORS["bg_medium"],
                     fg=COLORS["text_secondary"]).pack(padx=20, pady=20)
            return

        # Calculate overall stats
        total_marks = sum(r.marks for r in results)
        avg_marks = total_marks / len(results) if results else 0
        passed = sum(1 for r in results if r.marks >= 50)
        
        # Stats cards
        cards_row = tk.Frame(f, bg=COLORS["bg_medium"])
        cards_row.pack(fill="x", padx=20, pady=12)
        stat_items = [
            ("Total Subjects", str(len(results)), COLORS["primary"]),
            ("Average Score", f"{avg_marks:.1f}%", COLORS["secondary"]),
            ("Subjects Passed", f"{passed}/{len(results)}", COLORS["success"]),
        ]
        for i, (label, val, color) in enumerate(stat_items):
            card = tk.Frame(cards_row, bg=color, padx=20, pady=16)
            card.grid(row=0, column=i, padx=8, sticky="ew")
            cards_row.columnconfigure(i, weight=1)
            tk.Label(card, text=str(val), font=("Segoe UI", 24, "bold"),
                     bg=color, fg="white").pack()
            tk.Label(card, text=label, font=FONTS["small"],
                     bg=color, fg="#d0d8ff").pack()

        # Results table
        tk.Label(f, text="Subject Results", font=FONTS["subheading"],
                 bg=COLORS["bg_medium"], fg=COLORS["text_primary"]).pack(anchor="w", padx=20, pady=(16, 8))

        cols = ("subject", "class", "marks", "grade", "remarks")
        headings = ("Subject", "Class", "Marks", "Grade", "Remarks")
        tree_frame = tk.Frame(f, bg=COLORS["bg_medium"])
        tree_frame.pack(fill="both", expand=True, padx=20, pady=8)
        
        tree = ttk.Treeview(tree_frame, columns=cols, show="headings", height=10)
        for col, head in zip(cols, headings):
            tree.heading(col, text=head)
            tree.column(col, width=150 if col != "remarks" else 200)
        tree.pack(side="left", fill="both", expand=True)
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=tree.yview)
        scrollbar.pack(side="right", fill="y")
        tree.configure(yscrollcommand=scrollbar.set)

        # Grade scale
        grade_scale = [
            (80, 100, "A", "Distinction"),
            (70, 79, "B", "Credit"),
            (60, 69, "C", "Merit"),
            (50, 59, "D", "Pass"),
            (0, 49, "F", "Fail"),
        ]

        for r in results:
            subject = r.subject.subject_name if r.subject else "N/A"
            class_name = r.subject.class_.class_name if r.subject and r.subject.class_ else "N/A"
            marks = r.marks
            
            # Determine grade
            grade = "F"
            remarks = "Fail"
            for min_val, max_val, g, rem in grade_scale:
                if min_val <= marks <= max_val:
                    grade = g
                    remarks = rem
                    break
            
            tree.insert("", "end", values=(subject, class_name, f"{marks}", grade, remarks))

    def _show_profile(self):
        self.update_section_title("My Profile")
        f = self.get_content_frame()
        
        profile_card = tk.Frame(f, bg=COLORS["card"], padx=30, pady=25,
                                highlightbackground=COLORS["border"], highlightthickness=1)
        profile_card.pack(fill="x", padx=20, pady=20)
        
        tk.Label(profile_card, text="Student Information",
                 font=FONTS["subheading"], bg=COLORS["card"],
                 fg=COLORS["text_primary"]).pack(anchor="w", pady=(0, 16))
        
        info_items = [
            ("Admission Number", self.user.admission_number),
            ("Full Name", self.user.full_name),
            ("Gender", self.user.gender),
            ("Date of Birth", str(self.user.date_of_birth) if self.user.date_of_birth else "Not set"),
            ("Class", self.user.class_.class_name if self.user.class_ else "Not assigned"),
        ]
        
        for label, value in info_items:
            row = tk.Frame(profile_card, bg=COLORS["card"])
            row.pack(fill="x", pady=4)
            tk.Label(row, text=f"{label}:", font=FONTS["body_bold"],
                     bg=COLORS["card"], fg=COLORS["text_secondary"],
                     width=18, anchor="w").pack(side="left")
            tk.Label(row, text=str(value), font=FONTS["body"],
                     bg=COLORS["card"], fg=COLORS["text_primary"]).pack(side="left")
