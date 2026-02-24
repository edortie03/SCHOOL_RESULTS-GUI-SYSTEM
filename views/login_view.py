"""
views/login_view.py - Secure login screen with registration
"""
import tkinter as tk
from tkinter import ttk
from config import COLORS, FONTS, APP_TITLE, SessionLocal
from utils.ui_helpers import make_label, make_entry, center_window, show_error
from services.auth_service import AuthService
from services.student_service import StudentService


class LoginView(tk.Toplevel):
    def __init__(self, master, on_login_success):
        super().__init__(master)
        self.on_login_success = on_login_success
        self.title("Login — " + APP_TITLE)
        self.resizable(False, False)
        self.configure(bg=COLORS["bg_dark"])
        self.protocol("WM_DELETE_WINDOW", self.master.destroy)
        center_window(self, 440, 580)
        self._build()
        self.grab_set()

    def _build(self):
        bg = COLORS["bg_dark"]
        card_bg = COLORS["card"]
        # Outer padding
        outer = tk.Frame(self, bg=bg, padx=40, pady=30)
        outer.pack(fill="both", expand=True)

        # Logo / title area
        tk.Label(outer, text="🎓", font=("Segoe UI Emoji", 42), bg=bg,
                 fg=COLORS["primary_light"]).pack(pady=(0, 8))
        tk.Label(outer, text="School Results System",
                 font=FONTS["heading"], bg=bg, fg=COLORS["white"]).pack()
        tk.Label(outer, text="Sign in to your account",
                 font=FONTS["small"], bg=bg, fg=COLORS["text_secondary"]).pack(pady=(4, 24))

        # Notebook for Login/Register tabs
        self.notebook = ttk.Notebook(outer)
        self.notebook.pack(fill="both", expand=True)
        
        # Login tab
        self.login_frame = tk.Frame(self.notebook, bg=card_bg, padx=30, pady=20)
        self.notebook.add(self.login_frame, text="  Login  ")
        self._build_login_tab()
        
        # Teacher Registration tab
        self.teacher_reg_frame = tk.Frame(self.notebook, bg=card_bg, padx=30, pady=20)
        self.notebook.add(self.teacher_reg_frame, text="  Register as Teacher  ")
        self._build_teacher_reg_tab()
        
        # Student Registration tab
        self.student_reg_frame = tk.Frame(self.notebook, bg=card_bg, padx=30, pady=20)
        self.notebook.add(self.student_reg_frame, text="  Register as Student  ")
        self._build_student_reg_tab()

        # Footer hint
        tk.Label(outer, text="Default admin: admin@school.edu / Admin@1234",
                 font=FONTS["small"], bg=bg, fg=COLORS["text_secondary"]).pack(pady=(16, 0))

    def _build_login_tab(self):
        card = self.login_frame
        
        # Login type selector
        tk.Label(card, text="Login Type", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        self.login_type_var = tk.StringVar(value="email")
        type_frame = tk.Frame(card, bg=card["bg"])
        type_frame.pack(fill="x", pady=(4, 14))
        tk.Radiobutton(type_frame, text="Email (Admin/Teacher)", variable=self.login_type_var, 
                       value="email", bg=card["bg"], fg=COLORS["text_primary"],
                       selectcolor=COLORS["bg_medium"],
                       command=self._update_login_placeholder).pack(side="left")
        tk.Radiobutton(type_frame, text="Admission No (Student)", variable=self.login_type_var,
                       value="admission", bg=card["bg"], fg=COLORS["text_primary"],
                       selectcolor=COLORS["bg_medium"],
                       command=self._update_login_placeholder).pack(side="left", padx=10)
        
        # Username (Email or Admission Number)
        self.user_label = tk.Label(card, text="Email Address", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"])
        self.user_label.pack(anchor="w")
        self.user_var = tk.StringVar()
        self.user_entry = make_entry(card, textvariable=self.user_var, width=35)
        self.user_entry.configure(bg=COLORS["bg_medium"])
        self.user_entry.pack(fill="x", pady=(4, 14))

        # Password
        tk.Label(card, text="Password", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        self.pass_var = tk.StringVar()
        pass_entry = make_entry(card, textvariable=self.pass_var, width=35, show="•")
        pass_entry.configure(bg=COLORS["bg_medium"])
        pass_entry.pack(fill="x", pady=(4, 20))

        # Login button
        login_btn = tk.Button(
            card, text="Sign In", font=FONTS["body_bold"],
            bg=COLORS["primary"], fg=COLORS["white"],
            activebackground=COLORS["primary_light"], activeforeground=COLORS["white"],
            relief="flat", cursor="hand2", pady=8,
            command=self._do_login,
        )
        login_btn.pack(fill="x")

        # Bind Enter key
        self.bind("<Return>", lambda e: self._do_login())
        self.user_entry.focus_set()

    def _update_login_placeholder(self):
        login_type = self.login_type_var.get()
        if login_type == "email":
            self.user_label.config(text="Email Address")
            self.user_entry.delete(0, tk.END)
            self.user_var.set("")
        else:
            self.user_label.config(text="Admission Number")
            self.user_entry.delete(0, tk.END)
            self.user_var.set("")

    def _build_teacher_reg_tab(self):
        card = self.teacher_reg_frame
        
        # Full Name
        tk.Label(card, text="Full Name", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        self.teacher_name_var = tk.StringVar()
        name_entry = make_entry(card, textvariable=self.teacher_name_var, width=35)
        name_entry.configure(bg=COLORS["bg_medium"])
        name_entry.pack(fill="x", pady=(4, 14))

        # Email
        tk.Label(card, text="Email Address", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        self.teacher_email_var = tk.StringVar()
        email_entry = make_entry(card, textvariable=self.teacher_email_var, width=35)
        email_entry.configure(bg=COLORS["bg_medium"])
        email_entry.pack(fill="x", pady=(4, 14))

        # Password
        tk.Label(card, text="Password", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        self.teacher_pass_var = tk.StringVar()
        pass_entry = make_entry(card, textvariable=self.teacher_pass_var, width=35, show="•")
        pass_entry.configure(bg=COLORS["bg_medium"])
        pass_entry.pack(fill="x", pady=(4, 14))

        # Confirm Password
        tk.Label(card, text="Confirm Password", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        self.teacher_confirm_var = tk.StringVar()
        confirm_entry = make_entry(card, textvariable=self.teacher_confirm_var, width=35, show="•")
        confirm_entry.configure(bg=COLORS["bg_medium"])
        confirm_entry.pack(fill="x", pady=(4, 20))

        # Register button
        register_btn = tk.Button(
            card, text="Register as Teacher", font=FONTS["body_bold"],
            bg=COLORS["success"], fg=COLORS["white"],
            activebackground=COLORS["primary_light"], activeforeground=COLORS["white"],
            relief="flat", cursor="hand2", pady=8,
            command=self._do_teacher_register,
        )
        register_btn.pack(fill="x")

    def _build_student_reg_tab(self):
        card = self.student_reg_frame
        
        # Admission Number
        tk.Label(card, text="Admission Number", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        self.student_adm_var = tk.StringVar()
        adm_entry = make_entry(card, textvariable=self.student_adm_var, width=35)
        adm_entry.configure(bg=COLORS["bg_medium"])
        adm_entry.pack(fill="x", pady=(4, 14))

        # First Name
        tk.Label(card, text="First Name", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        self.student_first_var = tk.StringVar()
        first_entry = make_entry(card, textvariable=self.student_first_var, width=35)
        first_entry.configure(bg=COLORS["bg_medium"])
        first_entry.pack(fill="x", pady=(4, 14))

        # Last Name
        tk.Label(card, text="Last Name", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        self.student_last_var = tk.StringVar()
        last_entry = make_entry(card, textvariable=self.student_last_var, width=35)
        last_entry.configure(bg=COLORS["bg_medium"])
        last_entry.pack(fill="x", pady=(4, 14))

        # Gender
        tk.Label(card, text="Gender", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        self.student_gender_var = tk.StringVar()
        gender_combo = ttk.Combobox(card, textvariable=self.student_gender_var, width=32)
        gender_combo['values'] = ('Male', 'Female', 'Other')
        gender_combo['state'] = 'readonly'
        gender_combo.configure(background=COLORS["bg_medium"])
        gender_combo.pack(fill="x", pady=(4, 14))

        # Password
        tk.Label(card, text="Password", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        self.student_pass_var = tk.StringVar()
        pass_entry = make_entry(card, textvariable=self.student_pass_var, width=35, show="•")
        pass_entry.configure(bg=COLORS["bg_medium"])
        pass_entry.pack(fill="x", pady=(4, 14))

        # Confirm Password
        tk.Label(card, text="Confirm Password", font=FONTS["body_bold"],
                 bg=card["bg"], fg=COLORS["text_secondary"]).pack(anchor="w")
        self.student_confirm_var = tk.StringVar()
        confirm_entry = make_entry(card, textvariable=self.student_confirm_var, width=35, show="•")
        confirm_entry.configure(bg=COLORS["bg_medium"])
        confirm_entry.pack(fill="x", pady=(4, 20))

        # Register button
        register_btn = tk.Button(
            card, text="Register as Student", font=FONTS["body_bold"],
            bg=COLORS["success"], fg=COLORS["white"],
            activebackground=COLORS["primary_light"], activeforeground=COLORS["white"],
            relief="flat", cursor="hand2", pady=8,
            command=self._do_student_register,
        )
        register_btn.pack(fill="x")

    def _do_login(self):
        user_input = self.user_var.get().strip()
        password = self.pass_var.get().strip()
        
        if not user_input or not password:
            show_error("Validation", "Please enter both credentials.")
            return
        
        # Determine login type
        login_type = self.login_type_var.get()
        
        if login_type == "admission":
            # Student login - use admission number
            self.on_login_success("", password, admission_number=user_input)
        else:
            # Email login - admin/teacher
            self.on_login_success(user_input, password)

    def _do_teacher_register(self):
        name = self.teacher_name_var.get().strip()
        email = self.teacher_email_var.get().strip()
        password = self.teacher_pass_var.get().strip()
        confirm = self.teacher_confirm_var.get().strip()

        if not name or not email or not password:
            show_error("Validation", "All fields are required.")
            return
        if password != confirm:
            show_error("Validation", "Passwords do not match.")
            return
        if len(password) < 6:
            show_error("Validation", "Password must be at least 6 characters.")
            return

        db = SessionLocal()
        try:
            auth_svc = AuthService(db)
            auth_svc.create_teacher(name, email, password)
            from tkinter import messagebox
            messagebox.showinfo("Success", "Teacher registered successfully! Please login.")
            self.notebook.select(0)  # Switch to login tab
            self.user_var.set(email)
            self.teacher_name_var.set("")
            self.teacher_email_var.set("")
            self.teacher_pass_var.set("")
            self.teacher_confirm_var.set("")
        except Exception as e:
            show_error("Registration Error", str(e))
        finally:
            db.close()

    def _do_student_register(self):
        adm_number = self.student_adm_var.get().strip()
        first_name = self.student_first_var.get().strip()
        last_name = self.student_last_var.get().strip()
        gender = self.student_gender_var.get().strip()
        password = self.student_pass_var.get().strip()
        confirm = self.student_confirm_var.get().strip()

        if not adm_number or not first_name or not last_name or not gender or not password:
            show_error("Validation", "All fields are required.")
            return
        if password != confirm:
            show_error("Validation", "Passwords do not match.")
            return
        if len(password) < 6:
            show_error("Validation", "Password must be at least 6 characters.")
            return

        db = SessionLocal()
        try:
            # Create student with password hash
            student_svc = StudentService(db)
            password_hash = AuthService.hash_password(password)
            student_svc.create(
                admission_number=adm_number,
                first_name=first_name,
                last_name=last_name,
                gender=gender,
                class_id=None,
                password_hash=password_hash
            )
            
            from tkinter import messagebox
            messagebox.showinfo("Success", "Student registered successfully! Please login with your admission number.")
            self.student_adm_var.set("")
            self.student_first_var.set("")
            self.student_last_var.set("")
            self.student_gender_var.set("")
            self.student_pass_var.set("")
            self.student_confirm_var.set("")
        except Exception as e:
            show_error("Registration Error", str(e))
        finally:
            db.close()
