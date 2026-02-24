"""
main.py - Application entry point
School Examination Results Management System
"""
import tkinter as tk
from tkinter import ttk, messagebox
import logging
import sys

# ── Bootstrap ─────────────────────────────────────────────────────────────────
from config import init_db, SessionLocal, COLORS, FONTS, APP_TITLE, WINDOW_SIZE
from utils.ui_helpers import apply_treeview_style, center_window
from services.auth_service import AuthService

logger = logging.getLogger(__name__)


class Application(tk.Tk):
    """Root application controller."""

    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry(WINDOW_SIZE)
        self.configure(bg=COLORS["bg_medium"])
        self.minsize(1024, 680)
        center_window(self, 1280, 780)

        # Apply global ttk styles
        style = ttk.Style(self)
        apply_treeview_style(style)

        # Initialise database
        try:
            init_db()
        except Exception as e:
            messagebox.showerror(
                "Database Error",
                f"Could not connect to the database.\n\n{e}\n\n"
                "Please check your .env file and ensure PostgreSQL is running."
            )
            self.destroy()
            sys.exit(1)

        # Seed default admin if needed
        db = SessionLocal()
        try:
            AuthService(db).seed_default_admin()
        finally:
            db.close()

        self._current_dashboard = None
        self._show_login()

    # ── Login flow ────────────────────────────────────────────────────────────

    def _show_login(self):
        # Hide root window; show login Toplevel
        self.withdraw()
        from views.login_view import LoginView
        LoginView(self, on_login_success=self._authenticate)

    def _authenticate(self, email: str, password: str, admission_number: str = None):
        db = SessionLocal()
        try:
            user, role = AuthService(db).login(email, password, admission_number)
        finally:
            db.close()

        if not user:
            messagebox.showerror("Login Failed",
                                 "Invalid credentials. Please try again.")
            return

        # Close login window
        for widget in self.winfo_children():
            if isinstance(widget, tk.Toplevel):
                widget.destroy()

        self._launch_dashboard(user, role)

    def _launch_dashboard(self, user, role: str):
        self.deiconify()
        # Clear old dashboard if any
        for widget in self.winfo_children():
            widget.destroy()

        if role == "ADMIN":
            from views.admin_dashboard import AdminDashboard
            self._current_dashboard = AdminDashboard(
                self, user, logout_callback=self._logout)
        elif role == "TEACHER":
            from views.teacher_dashboard import TeacherDashboard
            self._current_dashboard = TeacherDashboard(
                self, user, logout_callback=self._logout)
        elif role == "STUDENT":
            from views.student_dashboard import StudentDashboard
            self._current_dashboard = StudentDashboard(
                self, user, logout_callback=self._logout)
        else:
            messagebox.showerror("Access Denied", f"Unknown role: {role}")
            self._logout()

    def _logout(self):
        if self._current_dashboard:
            # Close any open db sessions
            if hasattr(self._current_dashboard, "_db"):
                try:
                    self._current_dashboard._db.close()
                except Exception:
                    pass
        for widget in self.winfo_children():
            widget.destroy()
        self._current_dashboard = None
        self._show_login()


def main():
    app = Application()
    app.mainloop()


if __name__ == "__main__":
    main()
