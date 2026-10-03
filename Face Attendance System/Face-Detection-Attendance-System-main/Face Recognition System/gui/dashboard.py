"""
Main GUI Dashboard
Primary user interface for the Face Recognition Attendance System.
"""

import logging
import threading
import tkinter as tk
from tkinter import messagebox, ttk

from config import SIDEBAR_WIDTH, WINDOW_HEIGHT, WINDOW_WIDTH
from gui.theme import (
    BUTTON_STYLE,
    DANGER_BUTTON_STYLE,
    ENTRY_STYLE,
    FRAME_STYLE,
    LABEL_STYLE,
    SIDEBAR_FRAME_STYLE,
    TITLE_LABEL_STYLE,
    Theme,
)
from modules.attendance import attendance_system
from modules.export import csv_exporter
from modules.registration import face_registration
from modules.trainer import face_trainer
from utils.database import db_manager
from utils.utils import get_current_date, get_current_time

logger = logging.getLogger(__name__)


class FaceAttendanceDashboard:
    """
    Main GUI dashboard for the attendance system.
    """

    def __init__(self, root):
        """Initialize dashboard."""
        self.root = root
        self.root.title("Face Recognition Attendance System")
        self.root.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")
        self.root.configure(bg=Theme.BG)
        self.root.minsize(1050, 700)
        self.current_page = None
        self.is_running = True

        self.setup_ui()
        self.update_clock()

    @staticmethod
    def merge_style(base_style, **overrides):
        """Return a Tkinter style dict with overrides applied once."""
        style = dict(base_style)
        style.update(overrides)
        return style

    def setup_ui(self):
        """Set up main layout."""
        self.sidebar = tk.Frame(self.root, width=SIDEBAR_WIDTH, **SIDEBAR_FRAME_STYLE)
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        self.sidebar.pack_propagate(False)

        self.content_frame = tk.Frame(self.root, **FRAME_STYLE)
        self.content_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        self.create_sidebar()
        self.show_home_page()

    def create_sidebar(self):
        """Create sidebar navigation."""
        tk.Label(
            self.sidebar,
            text="FR Attendance",
            font=("Segoe UI", 16, "bold"),
            **SIDEBAR_FRAME_STYLE,
        ).pack(pady=(22, 4), padx=10)

        tk.Label(
            self.sidebar,
            text="Face Recognition",
            font=("Segoe UI", 9),
            **self.merge_style(SIDEBAR_FRAME_STYLE, fg=Theme.TEXT_SECONDARY),
        ).pack(padx=10, pady=(0, 20))

        tk.Frame(self.sidebar, bg=Theme.BORDER, height=1).pack(fill=tk.X, padx=10, pady=10)

        buttons = [
            ("Home", self.show_home_page),
            ("Register User", self.show_registration_page),
            ("Train Model", self.show_training_page),
            ("Start Attendance", self.show_attendance_page),
            ("View Users", self.show_users_page),
            ("View Attendance", self.show_attendance_view_page),
            ("Analytics", self.show_analytics_page),
            ("Export Data", self.show_export_page),
            ("Settings", self.show_settings_page),
        ]

        for text, command in buttons:
            tk.Button(
                self.sidebar,
                text=text,
                command=command,
                font=("Segoe UI", 10),
                bg=Theme.SIDEBAR,
                fg=Theme.TEXT,
                activebackground=Theme.ACCENT,
                activeforeground=Theme.TEXT,
                bd=0,
                anchor=tk.W,
                padx=15,
                pady=12,
                cursor="hand2",
            ).pack(fill=tk.X, padx=5, pady=3)

        tk.Frame(self.sidebar, bg=Theme.BORDER, height=1).pack(fill=tk.X, padx=10, pady=20)

        tk.Button(
            self.sidebar,
            text="Exit",
            command=self.exit_application,
            **DANGER_BUTTON_STYLE,
        ).pack(fill=tk.X, padx=5, pady=3)

    def clear_content(self):
        """Clear the content frame."""
        for widget in self.content_frame.winfo_children():
            widget.destroy()

    def page_title(self, text):
        """Add a page title."""
        tk.Label(
            self.content_frame,
            text=text,
            **self.merge_style(TITLE_LABEL_STYLE, font=("Segoe UI", 16, "bold")),
        ).pack(pady=20)

    def create_stat_card(self, parent, title, value, color):
        """Create a compact statistics card."""
        card = tk.Frame(parent, bg=color, relief=tk.RAISED, bd=0, width=180, height=105)
        card.pack_propagate(False)

        tk.Label(card, text=title, font=("Segoe UI", 10), bg=color, fg=Theme.TEXT).pack(pady=10)
        tk.Label(card, text=str(value), font=("Segoe UI", 22, "bold"), bg=color, fg=Theme.TEXT).pack()
        return card

    def run_background(self, target):
        """Run a callable on a daemon thread."""
        thread = threading.Thread(target=target, daemon=True)
        thread.start()
        return thread

    def show_home_page(self):
        """Show home/dashboard page."""
        self.current_page = "home"
        self.clear_content()

        top_panel = tk.Frame(self.content_frame, bg=Theme.SIDEBAR)
        top_panel.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(
            top_panel,
            text="Welcome to Face Recognition Attendance System",
            font=("Segoe UI", 20, "bold"),
            **SIDEBAR_FRAME_STYLE,
        ).pack(pady=(15, 8))

        self.datetime_label = tk.Label(
            top_panel,
            text=f"{get_current_date()} | {get_current_time()}",
            font=("Segoe UI", 12),
            **self.merge_style(SIDEBAR_FRAME_STYLE, fg=Theme.TEXT_SECONDARY),
        )
        self.datetime_label.pack(pady=(0, 18))

        stats_frame = tk.Frame(self.content_frame, **FRAME_STYLE)
        stats_frame.pack(fill=tk.X, padx=20, pady=20)

        users = db_manager.get_all_users()
        today_attendance = db_manager.get_today_attendance()
        stats = [
            ("Total Users", len(users), Theme.ACCENT),
            ("Today Present", len(today_attendance), Theme.SUCCESS),
            ("Model", "Trained" if face_trainer.is_model_trained() else "Not Trained", Theme.WARNING),
        ]

        for title, value, color in stats:
            self.create_stat_card(stats_frame, title, value, color).pack(side=tk.LEFT, padx=10, pady=10)

        actions_frame = tk.Frame(self.content_frame, **FRAME_STYLE)
        actions_frame.pack(fill=tk.X, padx=20, pady=20)

        tk.Label(
            actions_frame,
            text="Quick Actions",
            **self.merge_style(TITLE_LABEL_STYLE, font=("Segoe UI", 14, "bold")),
        ).pack(anchor=tk.W, pady=(0, 15))

        for text, command in [
            ("Register New User", self.show_registration_page),
            ("Train Model", self.show_training_page),
            ("Start Attendance", self.show_attendance_page),
        ]:
            tk.Button(actions_frame, text=text, command=command, **BUTTON_STYLE).pack(pady=5, anchor=tk.W)

    def show_registration_page(self):
        """Show user registration page."""
        self.current_page = "registration"
        self.clear_content()
        self.page_title("Register New User")

        form_frame = tk.Frame(self.content_frame, **FRAME_STYLE)
        form_frame.pack(padx=30, pady=20)

        fields = [
            ("Full Name:", "name"),
            ("Student ID:", "student_id"),
            ("Email:", "email"),
            ("Phone:", "phone"),
        ]
        entries = {}

        for row, (label, key) in enumerate(fields):
            tk.Label(form_frame, text=label, **LABEL_STYLE).grid(row=row, column=0, sticky=tk.W, pady=10)
            entry = tk.Entry(form_frame, **ENTRY_STYLE, width=34)
            entry.grid(row=row, column=1, padx=10, pady=10)
            entries[key] = entry

        status_label = tk.Label(
            form_frame,
            text="",
            **self.merge_style(LABEL_STYLE, fg=Theme.TEXT_SECONDARY),
        )
        status_label.grid(row=4, column=0, columnspan=2, pady=20)

        def register_user():
            name = entries["name"].get().strip()
            student_id = entries["student_id"].get().strip()
            email = entries["email"].get().strip() or None
            phone = entries["phone"].get().strip() or None

            if not name or not student_id:
                messagebox.showerror("Error", "Name and Student ID are required.")
                return

            register_btn.config(state=tk.DISABLED)
            status_label.config(text="Camera window is opening. Press SPACE to capture faces.")

            def worker():
                result = face_registration.register_user(name, student_id, email, phone)

                def finish():
                    register_btn.config(state=tk.NORMAL)
                    status_label.config(text="")
                    if result["success"]:
                        messagebox.showinfo("Success", result["message"])
                        for entry in entries.values():
                            entry.delete(0, tk.END)
                    else:
                        messagebox.showerror("Error", result["message"])

                self.root.after(0, finish)

            self.run_background(worker)

        register_btn = tk.Button(
            form_frame,
            text="Register and Capture Faces",
            command=register_user,
            **BUTTON_STYLE,
        )
        register_btn.grid(row=5, column=0, columnspan=2, pady=20)

    def show_training_page(self):
        """Show model training page."""
        self.current_page = "training"
        self.clear_content()
        self.page_title("Train Face Recognition Model")

        stats = face_registration.get_dataset_stats()
        info = (
            f"Current Dataset Statistics:\n\n"
            f"Total Users: {stats.get('total_users', 0)}\n"
            f"Total Images: {stats.get('total_images', 0)}\n"
            f"Avg Images per User: {stats.get('avg_images_per_user', 0)}\n\n"
            "Click Start Training after registering users."
        )

        tk.Label(
            self.content_frame,
            text=info,
            justify=tk.LEFT,
            **LABEL_STYLE,
        ).pack(padx=30, pady=20, anchor=tk.W)

        progress_frame = tk.Frame(self.content_frame, **FRAME_STYLE)
        progress_frame.pack(padx=30, pady=20, fill=tk.X)

        progress_label = tk.Label(progress_frame, text="", **LABEL_STYLE)
        progress_label.pack(anchor=tk.W)

        progress_bar = ttk.Progressbar(progress_frame, length=320, mode="indeterminate")
        progress_bar.pack(pady=10, anchor=tk.W)

        def train_model():
            train_btn.config(state=tk.DISABLED)
            progress_bar.start()
            progress_label.config(text="Training in progress...")

            def worker():
                result = face_trainer.train_model()

                def finish():
                    progress_bar.stop()
                    train_btn.config(state=tk.NORMAL)
                    progress_label.config(text="")
                    if result["success"]:
                        messagebox.showinfo("Success", result["message"])
                    else:
                        messagebox.showerror("Error", result["message"])

                self.root.after(0, finish)

            self.run_background(worker)

        train_btn = tk.Button(progress_frame, text="Start Training", command=train_model, **BUTTON_STYLE)
        train_btn.pack(pady=20, anchor=tk.W)

    def show_attendance_page(self):
        """Show attendance marking page."""
        self.current_page = "attendance"
        self.clear_content()

        if not face_trainer.is_model_trained():
            messagebox.showerror("Error", "Model not trained. Please train the model first.")
            self.show_home_page()
            return

        self.page_title("Start Real-Time Attendance")
        tk.Label(
            self.content_frame,
            text="Webcam window will open. Press ESC in that window to stop recognition.",
            **LABEL_STYLE,
        ).pack(pady=10)

        stats_frame = tk.Frame(self.content_frame, **FRAME_STYLE)
        stats_frame.pack(padx=30, pady=20, fill=tk.X)

        stat_labels = {}
        for stat_name in ["Recognized", "Unknown", "Faces in Frame"]:
            label_frame = tk.Frame(stats_frame, **FRAME_STYLE)
            label_frame.pack(side=tk.LEFT, padx=20)

            tk.Label(label_frame, text=f"{stat_name}:", **LABEL_STYLE).pack()
            value_label = tk.Label(
                label_frame,
                text="0",
                **self.merge_style(LABEL_STYLE, font=("Segoe UI", 18, "bold"), fg=Theme.ACCENT),
            )
            value_label.pack()
            stat_labels[stat_name] = value_label

        button_frame = tk.Frame(self.content_frame, **FRAME_STYLE)
        button_frame.pack(pady=20)

        def start_attendance():
            start_btn.config(state=tk.DISABLED)
            stop_btn.config(state=tk.NORMAL)

            def update_stats(data):
                def apply_update():
                    stat_labels["Recognized"].config(text=str(data["recognized"]))
                    stat_labels["Unknown"].config(text=str(data["unknown"]))
                    stat_labels["Faces in Frame"].config(text=str(data["face_count"]))

                self.root.after(0, apply_update)

            def worker():
                result = attendance_system.start_recognition(process_callback=update_stats)

                def finish():
                    start_btn.config(state=tk.NORMAL)
                    stop_btn.config(state=tk.DISABLED)
                    if result["success"]:
                        messagebox.showinfo(
                            "Session Complete",
                            f"Recognized detections: {result.get('recognized_count', 0)}\n"
                            f"Unknown detections: {result.get('unknown_count', 0)}",
                        )
                    else:
                        messagebox.showerror("Error", result["message"])

                self.root.after(0, finish)

            self.run_background(worker)

        def stop_attendance():
            attendance_system.stop_recognition()

        start_btn = tk.Button(button_frame, text="Start Recognition", command=start_attendance, **BUTTON_STYLE)
        start_btn.pack(side=tk.LEFT, padx=10)

        stop_btn = tk.Button(
            button_frame,
            text="Stop Recognition",
            command=stop_attendance,
            state=tk.DISABLED,
            **DANGER_BUTTON_STYLE,
        )
        stop_btn.pack(side=tk.LEFT, padx=10)

    def show_users_page(self):
        """Show registered users page."""
        self.current_page = "users"
        self.clear_content()
        self.page_title("Registered Users")

        users = db_manager.get_all_users()
        if not users:
            tk.Label(self.content_frame, text="No users registered yet.", **LABEL_STYLE).pack(pady=20)
            return

        tree = self.create_tree(
            columns=("Name", "Student ID", "Email", "Phone", "Registered"),
            widths=(160, 120, 220, 130, 150),
        )

        for user in users:
            tree.insert(
                "",
                tk.END,
                values=(
                    user.get("name", ""),
                    user.get("student_id", ""),
                    user.get("email", ""),
                    user.get("phone", ""),
                    user.get("created_at", "")[:10],
                ),
            )

    def show_attendance_view_page(self):
        """Show attendance records page."""
        self.current_page = "attendance_view"
        self.clear_content()
        self.page_title("Attendance Records")

        filter_frame = tk.Frame(self.content_frame, **FRAME_STYLE)
        filter_frame.pack(padx=20, pady=10, fill=tk.X)

        tk.Label(filter_frame, text="Show:", **LABEL_STYLE).pack(side=tk.LEFT, padx=5)
        selection_var = tk.StringVar(value="today")
        for text, value in [("Today", "today"), ("This Week", "week"), ("This Month", "month"), ("All", "all")]:
            tk.Radiobutton(
                filter_frame,
                text=text,
                variable=selection_var,
                value=value,
                selectcolor=Theme.SIDEBAR,
                **LABEL_STYLE,
            ).pack(side=tk.LEFT, padx=10)

        tree = self.create_tree(
            columns=("Name", "Student ID", "Date", "Time", "Status", "Confidence"),
            widths=(150, 110, 110, 100, 100, 110),
        )

        def refresh_list(*_):
            for item in tree.get_children():
                tree.delete(item)

            import datetime as dt

            today = get_current_date()
            selection = selection_var.get()
            if selection == "today":
                records = db_manager.get_today_attendance()
            elif selection == "week":
                start_date = (dt.datetime.now() - dt.timedelta(days=7)).strftime("%Y-%m-%d")
                records = db_manager.get_attendance_by_date_range(start_date, today)
            elif selection == "month":
                start_date = (dt.datetime.now() - dt.timedelta(days=30)).strftime("%Y-%m-%d")
                records = db_manager.get_attendance_by_date_range(start_date, today)
            else:
                records = db_manager.get_attendance_by_date_range("2000-01-01", today)

            for record in records:
                tree.insert(
                    "",
                    tk.END,
                    values=(
                        record.get("name", ""),
                        record.get("student_id", ""),
                        record.get("date", ""),
                        record.get("time", ""),
                        record.get("status", ""),
                        f"{record.get('confidence', 0) * 100:.1f}%",
                    ),
                )

        selection_var.trace_add("write", refresh_list)
        refresh_list()

    def show_analytics_page(self):
        """Show attendance analytics page."""
        self.current_page = "analytics"
        self.clear_content()
        self.page_title("Attendance Analytics")

        stats = db_manager.get_attendance_statistics(get_current_date(), get_current_date())
        total_users = len(db_manager.get_all_users())
        present = stats.get("total_present", 0)

        analytics_frame = tk.Frame(self.content_frame, **FRAME_STYLE)
        analytics_frame.pack(padx=30, pady=20)

        for title, value, color in [
            ("Present Today", present, Theme.SUCCESS),
            ("Absent Today", max(0, total_users - present), Theme.DANGER),
            ("Late Today", stats.get("total_late", 0), Theme.WARNING),
            ("Total Records", stats.get("total_records", 0), Theme.ACCENT),
        ]:
            self.create_stat_card(analytics_frame, title, value, color).pack(side=tk.LEFT, padx=15, pady=10)

    def show_export_page(self):
        """Show export page."""
        self.current_page = "export"
        self.clear_content()
        self.page_title("Export Data")

        button_frame = tk.Frame(self.content_frame, **FRAME_STYLE)
        button_frame.pack(padx=30, pady=20)

        def show_result(result):
            if result["success"]:
                messagebox.showinfo("Success", f"{result['message']}\nFile: {result['filepath']}")
            else:
                messagebox.showerror("Error", result["message"])

        actions = [
            ("Export Today's Attendance", lambda: show_result(csv_exporter.export_attendance())),
            ("Export All Users", lambda: show_result(csv_exporter.export_users())),
            ("Export Attendance Summary", lambda: show_result(csv_exporter.export_attendance_summary())),
        ]

        for text, command in actions:
            tk.Button(button_frame, text=text, command=command, width=30, **BUTTON_STYLE).pack(pady=10)

    def show_settings_page(self):
        """Show settings page."""
        self.current_page = "settings"
        self.clear_content()
        self.page_title("Settings")

        settings_frame = tk.Frame(self.content_frame, **FRAME_STYLE)
        settings_frame.pack(padx=30, pady=20)

        def delete_model():
            deleted = face_trainer.delete_trained_model()
            messagebox.showinfo("Model", "Trained model deleted." if deleted else "No trained model found.")

        def optimize_database():
            db_manager.vacuum_database()
            messagebox.showinfo("Success", "Database optimized.")

        def clear_database():
            if messagebox.askyesno("Confirm", "Clear all database records? This cannot be undone."):
                db_manager.clear_all_data()
                messagebox.showinfo("Success", "Database records cleared.")

        for text, command in [
            ("Delete Trained Model", delete_model),
            ("Optimize Database", optimize_database),
            ("Clear Database Records", clear_database),
        ]:
            tk.Button(settings_frame, text=text, command=command, width=30, **DANGER_BUTTON_STYLE).pack(pady=10)

    def create_tree(self, columns, widths):
        """Create a scrollable Treeview in the content frame."""
        tree_frame = tk.Frame(self.content_frame, **FRAME_STYLE)
        tree_frame.pack(padx=20, pady=20, fill=tk.BOTH, expand=True)

        scrollbar = ttk.Scrollbar(tree_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        tree = ttk.Treeview(tree_frame, columns=columns, height=15, yscrollcommand=scrollbar.set)
        scrollbar.config(command=tree.yview)

        tree.column("#0", width=0, stretch=tk.NO)
        tree.heading("#0", text="")

        for column, width in zip(columns, widths):
            tree.column(column, anchor=tk.W, width=width)
            tree.heading(column, text=column, anchor=tk.W)

        tree.pack(fill=tk.BOTH, expand=True)
        return tree

    def update_clock(self):
        """Update dashboard clock."""
        if self.current_page == "home" and hasattr(self, "datetime_label"):
            self.datetime_label.config(text=f"{get_current_date()} | {get_current_time()}")

        if self.is_running:
            self.root.after(1000, self.update_clock)

    def exit_application(self):
        """Exit application."""
        if messagebox.askyesno("Exit", "Are you sure you want to exit?"):
            self.is_running = False
            attendance_system.stop_recognition()
            self.root.quit()
            self.root.destroy()


def main():
    """Start the application."""
    root = tk.Tk()
    FaceAttendanceDashboard(root)
    root.mainloop()


if __name__ == "__main__":
    main()
