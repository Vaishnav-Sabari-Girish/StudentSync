import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, font
import subprocess
import json
import os
import atexit
import signal
import time

class ProductivityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Productivity App")
        self.root.geometry("600x500")
        self.is_dark_mode = False
        self.current_user = None
        self.backend_processes = []
        self.timer_running = False
        self.timer_seconds = 25 * 60  # Default to 25 minutes
        self.pomodoro_count = 0
        self.task_checkboxes = {}  # Store checkbox states for tasks
        self.habit_checkboxes = {}  # Store checkbox states for habits

        # Define custom fonts
        self.ui_font = font.Font(family="Helvetica", size=14)
        self.timer_font = font.Font(family="Helvetica", size=36)

        # Register cleanup on exit
        atexit.register(self.cleanup)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Setup GUI
        self.setup_gui()
        self.apply_light_mode()

    def setup_gui(self):
        # Main container
        self.main_frame = ttk.Frame(self.root, padding=10)
        self.main_frame.pack(fill="both", expand=True)

        # Login Frame
        self.login_frame = ttk.Frame(self.main_frame, padding=10)
        self.login_frame.pack(fill="both", expand=True)

        ttk.Label(self.login_frame, text="Username:", font=self.ui_font).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.username_entry = ttk.Entry(self.login_frame, font=self.ui_font)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.login_frame, text="Password:", font=self.ui_font).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = ttk.Entry(self.login_frame, show="*", font=self.ui_font)
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self.login_frame, text="Register", command=self.register, style="TButton").grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self.login_frame, text="Login", command=self.login, style="TButton").grid(row=2, column=1, padx=5, pady=5)

        # Notebook for tabs (hidden initially)
        self.notebook = ttk.Notebook(self.main_frame)
        self.tasks_tab = ttk.Frame(self.notebook)
        self.timer_tab = ttk.Frame(self.notebook)
        self.habits_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.tasks_tab, text="Tasks")
        self.notebook.add(self.timer_tab, text="Focus Timer")
        self.notebook.add(self.habits_tab, text="Habit Planner")
        self.notebook.pack_forget()

        # Tasks Tab
        self.task_progress_label = ttk.Label(self.tasks_tab, text="Progress: 0%", font=self.ui_font)
        self.task_progress_label.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="w")
        self.task_progress = ttk.Progressbar(self.tasks_tab, length=300, mode="determinate")
        self.task_progress.grid(row=0, column=3, padx=5, pady=5, sticky="e")

        ttk.Label(self.tasks_tab, text="Task:", font=self.ui_font).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.task_entry = ttk.Entry(self.tasks_tab, font=self.ui_font)
        self.task_entry.grid(row=1, column=1, columnspan=2, padx=5, pady=5, sticky="ew")

        ttk.Button(self.tasks_tab, text="Add Task", command=self.add_task, style="TButton").grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self.tasks_tab, text="Edit Task", command=self.edit_task, style="TButton").grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(self.tasks_tab, text="Delete Task", command=self.delete_task, style="TButton").grid(row=2, column=2, padx=5, pady=5)

        self.task_tree = ttk.Treeview(self.tasks_tab, columns=("ID", "Task", "Completed"), show="headings")
        self.task_tree.heading("ID", text="ID")
        self.task_tree.heading("Task", text="Task")
        self.task_tree.heading("Completed", text="Completed")
        self.task_tree.column("ID", width=50)
        self.task_tree.column("Task", width=300)
        self.task_tree.column("Completed", width=100)
        self.task_tree.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")
        self.task_tree.bind("<ButtonRelease-1>", self.toggle_task_completion)

        self.tasks_tab.grid_columnconfigure(1, weight=1)

        # Focus Timer Tab
        self.timer_progress_label = ttk.Label(self.timer_tab, text="Progress: 0%", font=self.ui_font)
        self.timer_progress_label.pack(pady=5)
        self.timer_progress = ttk.Progressbar(self.timer_tab, length=300, mode="determinate")
        self.timer_progress.pack(pady=5)

        self.timer_label = ttk.Label(self.timer_tab, text="25:00", font=self.timer_font)
        self.timer_label.pack(pady=20)

        ttk.Button(self.timer_tab, text="Start", command=self.start_timer, style="TButton").pack(pady=5)
        ttk.Button(self.timer_tab, text="Pause", command=self.pause_timer, style="TButton").pack(pady=5)
        ttk.Button(self.timer_tab, text="Reset", command=self.reset_timer, style="TButton").pack(pady=5)

        self.pomodoro_status = ttk.Label(self.timer_tab, text="Work Session (Pomodoro #1)", font=self.ui_font)
        self.pomodoro_status.pack(pady=10)

        # Habit Planner Tab
        self.habit_progress_label = ttk.Label(self.habits_tab, text="Progress: 0%", font=self.ui_font)
        self.habit_progress_label.grid(row=0, column=0, columnspan=3, padx=5, pady=5, sticky="w")
        self.habit_progress = ttk.Progressbar(self.habits_tab, length=300, mode="determinate")
        self.habit_progress.grid(row=0, column=3, padx=5, pady=5, sticky="e")

        ttk.Label(self.habits_tab, text="Routine:", font=self.ui_font).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.habit_entry = ttk.Entry(self.habits_tab, font=self.ui_font)
        self.habit_entry.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        ttk.Label(self.habits_tab, text="Time (min):", font=self.ui_font).grid(row=1, column=2, padx=5, pady=5, sticky="e")
        self.habit_time = ttk.Entry(self.habits_tab, width=5, font=self.ui_font)
        self.habit_time.grid(row=1, column=3, padx=5, pady=5)

        ttk.Button(self.habits_tab, text="Add Routine", command=self.add_habit, style="TButton").grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self.habits_tab, text="Edit Routine", command=self.edit_habit, style="TButton").grid(row=2, column=1, padx=5, pady=5)
        ttk.Button(self.habits_tab, text="Delete Routine", command=self.delete_habit, style="TButton").grid(row=2, column=2, padx=5, pady=5)

        self.habit_tree = ttk.Treeview(self.habits_tab, columns=("ID", "Routine", "Time", "Completed"), show="headings")
        self.habit_tree.heading("ID", text="ID")
        self.habit_tree.heading("Routine", text="Routine")
        self.habit_tree.heading("Time", text="Time (min)")
        self.habit_tree.heading("Completed", text="Completed")
        self.habit_tree.column("ID", width=50)
        self.habit_tree.column("Routine", width=200)
        self.habit_tree.column("Time", width=100)
        self.habit_tree.column("Completed", width=100)
        self.habit_tree.grid(row=3, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")
        self.habit_tree.bind("<ButtonRelease-1>", self.toggle_habit_completion)

        self.habits_tab.grid_columnconfigure(1, weight=1)

        # Theme Toggle
        self.theme_button = ttk.Button(self.main_frame, text="Toggle Dark Mode", command=self.toggle_theme, style="TButton")
        self.theme_button.pack(pady=5, anchor="e")

    def call_backend(self, args):
        try:
            process = subprocess.run(
                ["java", "-cp", ".", "Backend"] + args,
                capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)),
                timeout=5
            )
            return process.stdout.strip(), process.stderr.strip()
        except subprocess.TimeoutExpired:
            return "", "Backend operation timed out"
        except Exception as e:
            return "", str(e)

    def cleanup(self):
        for proc in self.backend_processes:
            try:
                os.kill(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        self.backend_processes.clear()

    def on_closing(self):
        self.cleanup()
        self.root.destroy()

    def register(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        stdout, stderr = self.call_backend(["register", username, password])
        if stderr:
            messagebox.showerror("Error", stderr)
        else:
            messagebox.showinfo("Success", stdout)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        if not username or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return
        stdout, stderr = self.call_backend(["login", username, password])
        if stderr:
            messagebox.showerror("Error", stderr)
        else:
            self.current_user = username
            self.login_frame.pack_forget()
            self.notebook.pack(fill="both", expand=True)
            self.load_tasks()
            self.load_habits()
            messagebox.showinfo("Success", stdout)

    def add_task(self):
        task = self.task_entry.get()
        if not task:
            messagebox.showerror("Error", "Please enter a task")
            return
        stdout, stderr = self.call_backend(["add", self.current_user, task])
        if stderr:
            messagebox.showerror("Error", stderr)
        else:
            self.task_entry.delete(0, tk.END)
            self.load_tasks()

    def edit_task(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a task to edit")
            return
        task_id = self.task_tree.item(selected)["values"][0]
        new_task = simpledialog.askstring("Edit Task", "New task description:", initialvalue=self.task_tree.item(selected)["values"][1], parent=self.root)
        if new_task:
            stdout, stderr = self.call_backend(["edit", self.current_user, str(task_id), new_task])
            if stderr:
                messagebox.showerror("Error", stderr)
            else:
                self.load_tasks()

    def toggle_task_completion(self, event):
        item = self.task_tree.identify_row(event.y)
        if not item:
            return
        column = self.task_tree.identify_column(event.x)
        if column == "#3":  # Completed column
            task_id = self.task_tree.item(item)["values"][0]
            current_state = self.task_checkboxes.get(task_id, False)
            new_state = not current_state
            stdout, stderr = self.call_backend(["change_status", self.current_user, str(task_id), str(new_state).lower()])
            if stderr:
                messagebox.showerror("Error", stderr)
            else:
                self.load_tasks()

    def delete_task(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a task to delete")
            return
        task_id = self.task_tree.item(selected)["values"][0]
        stdout, stderr = self.call_backend(["delete", self.current_user, str(task_id)])
        if stderr:
            messagebox.showerror("Error", stderr)
        else:
            self.load_tasks()

    def load_tasks(self):
        self.task_tree.delete(*self.task_tree.get_children())
        self.task_checkboxes.clear()
        stdout, stderr = self.call_backend(["list", self.current_user])
        if stderr:
            messagebox.showerror("Error", stderr)
        else:
            try:
                tasks = json.loads(stdout) if stdout else []
                completed_count = sum(1 for task in tasks if task["completed"])
                total_count = len(tasks)
                progress = (completed_count / total_count * 100) if total_count > 0 else 0
                self.task_progress["value"] = progress
                self.task_progress_label.config(text=f"Progress: {int(progress)}%")
                for task in tasks:
                    task_id = task["id"]
                    self.task_checkboxes[task_id] = task["completed"]
                    checkbox_char = "☑" if task["completed"] else "☐"
                    self.task_tree.insert("", tk.END, values=(task_id, task["description"], checkbox_char))
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Invalid response from backend")

    def start_timer(self):
        if not self.timer_running:
            self.timer_running = True
            self.update_timer()

    def pause_timer(self):
        self.timer_running = False

    def reset_timer(self):
        self.timer_running = False
        self.timer_seconds = 25 * 60 if self.pomodoro_count % 2 == 0 else 5 * 60
        self.update_timer_display()
        self.timer_progress["value"] = 0
        self.timer_progress_label.config(text="Progress: 0%")
        if self.pomodoro_count % 8 == 7:
            self.pomodoro_count = 0
            self.pomodoro_status.config(text="Work Session (Pomodoro #1)")
        else:
            self.pomodoro_status.config(text=f"{'Work Session' if self.pomodoro_count % 2 == 0 else 'Break'} (Pomodoro #{(self.pomodoro_count // 2) + 1})")

    def update_timer(self):
        if self.timer_running and self.timer_seconds > 0:
            self.timer_seconds -= 1
            self.update_timer_display()
            total_seconds = 25 * 60 if self.pomodoro_count % 2 == 0 else 5 * 60
            progress = ((total_seconds - self.timer_seconds) / total_seconds) * 100
            self.timer_progress["value"] = progress
            self.timer_progress_label.config(text=f"Progress: {int(progress)}%")
            self.root.after(1000, self.update_timer)
        elif self.timer_seconds == 0:
            self.timer_running = False
            self.pomodoro_count += 1
            if self.pomodoro_count % 8 == 0:
                self.timer_seconds = 15 * 60  # Long break after 4 pomodoros
                messagebox.showinfo("Timer", "Long break time (15 minutes)!")
            elif self.pomodoro_count % 2 == 0:
                self.timer_seconds = 25 * 60  # Work session
                messagebox.showinfo("Timer", "Time for a new work session!")
            else:
                self.timer_seconds = 5 * 60  # Short break
                messagebox.showinfo("Timer", "Take a 5-minute break!")
            self.update_timer_display()
            self.timer_progress["value"] = 100
            self.timer_progress_label.config(text="Progress: 100%")
            self.pomodoro_status.config(text=f"{'Work Session' if self.pomodoro_count % 2 == 0 else 'Break'} (Pomodoro #{(self.pomodoro_count // 2) + 1})")

    def update_timer_display(self):
        minutes = self.timer_seconds // 60
        seconds = self.timer_seconds % 60
        self.timer_label.config(text=f"{minutes:02d}:{seconds:02d}")

    def add_habit(self):
        routine = self.habit_entry.get()
        time_str = self.habit_time.get()
        if not routine or not time_str:
            messagebox.showerror("Error", "Please enter routine and time")
            return
        try:
            time_min = int(time_str)
            if time_min <= 0:
                raise ValueError("Time must be positive")
        except ValueError:
            messagebox.showerror("Error", "Invalid time format (use positive integers)")
            return
        stdout, stderr = self.call_backend(["add_habit", self.current_user, routine, str(time_min)])
        if stderr:
            messagebox.showerror("Error", stderr)
        else:
            self.habit_entry.delete(0, tk.END)
            self.habit_time.delete(0, tk.END)
            self.load_habits()

    def edit_habit(self):
        selected = self.habit_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a routine to edit")
            return
        habit_id = self.habit_tree.item(selected)["values"][0]
        current_routine = self.habit_tree.item(selected)["values"][1]
        current_time = self.habit_tree.item(selected)["values"][2]

        edit_dialog = tk.Toplevel(self.root)
        edit_dialog.title("Edit Routine")
        edit_dialog.geometry("300x150")
        edit_dialog.transient(self.root)
        edit_dialog.grab_set()

        ttk.Label(edit_dialog, text="Routine:", font=self.ui_font).grid(row=0, column=0, padx=5, pady=5, sticky="e")
        routine_entry = ttk.Entry(edit_dialog, font=self.ui_font)
        routine_entry.insert(0, current_routine)
        routine_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(edit_dialog, text="Time (min):", font=self.ui_font).grid(row=1, column=0, padx=5, pady=5, sticky="e")
        time_entry = ttk.Entry(edit_dialog, font=self.ui_font)
        time_entry.insert(0, str(current_time))
        time_entry.grid(row=1, column=1, padx=5, pady=5)

        def submit_edit():
            new_routine = routine_entry.get()
            new_time_str = time_entry.get()
            if not new_routine or not new_time_str:
                messagebox.showerror("Error", "Please enter routine and time")
                edit_dialog.destroy()
                return
            try:
                new_time = int(new_time_str)
                if new_time <= 0:
                    raise ValueError("Time must be positive")
            except ValueError:
                messagebox.showerror("Error", "Invalid time format (use positive integers)")
                edit_dialog.destroy()
                return
            stdout, stderr = self.call_backend(["edit_habit", self.current_user, str(habit_id), new_routine, str(new_time)])
            if stderr:
                messagebox.showerror("Error", stderr)
            else:
                self.load_habits()
            edit_dialog.destroy()

        ttk.Button(edit_dialog, text="Submit", command=submit_edit, style="TButton").grid(row=2, column=0, columnspan=2, pady=10)

    def toggle_habit_completion(self, event):
        item = self.habit_tree.identify_row(event.y)
        if not item:
            return
        column = self.habit_tree.identify_column(event.x)
        if column == "#4":  # Completed column
            habit_id = self.habit_tree.item(item)["values"][0]
            current_state = self.habit_checkboxes.get(habit_id, False)
            new_state = not current_state
            stdout, stderr = self.call_backend(["change_habit_status", self.current_user, str(habit_id), str(new_state).lower()])
            if stderr:
                messagebox.showerror("Error", stderr)
            else:
                self.load_habits()

    def delete_habit(self):
        selected = self.habit_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a routine to delete")
            return
        habit_id = self.habit_tree.item(selected)["values"][0]
        stdout, stderr = self.call_backend(["delete_habit", self.current_user, str(habit_id)])
        if stderr:
            messagebox.showerror("Error", stderr)
        else:
            self.load_habits()

    def load_habits(self):
        self.habit_tree.delete(*self.habit_tree.get_children())
        self.habit_checkboxes.clear()
        stdout, stderr = self.call_backend(["list_habits", self.current_user])
        if stderr:
            messagebox.showerror("Error", stderr)
        else:
            try:
                habits = json.loads(stdout) if stdout else []
                completed_count = sum(1 for habit in habits if habit["completed"])
                total_count = len(habits)
                progress = (completed_count / total_count * 100) if total_count > 0 else 0
                self.habit_progress["value"] = progress
                self.habit_progress_label.config(text=f"Progress: {int(progress)}%")
                for habit in habits:
                    habit_id = habit["id"]
                    self.habit_checkboxes[habit_id] = habit["completed"]
                    checkbox_char = "☑" if habit["completed"] else "☐"
                    self.habit_tree.insert("", tk.END, values=(habit_id, habit["routine"], habit["time"], checkbox_char))
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Invalid response from backend")

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self.apply_dark_mode()
        else:
            self.apply_light_mode()

    def apply_light_mode(self):
        self.root.configure(bg="white")
        self.main_frame.configure(style="Light.TFrame")
        self.login_frame.configure(style="Light.TFrame")
        self.tasks_tab.configure(style="Light.TFrame")
        self.timer_tab.configure(style="Light.TFrame")
        self.habits_tab.configure(style="Light.TFrame")
        style = ttk.Style()
        style.configure("Light.TFrame", background="white")
        style.configure("TLabel", background="white", foreground="black", font=self.ui_font)
        style.configure("TEntry", fieldbackground="white", foreground="black", font=self.ui_font)
        style.configure("TButton", font=self.ui_font)
        style.configure("Treeview", background="white", foreground="black", fieldbackground="white", font=self.ui_font)
        style.configure("Treeview.Heading", font=self.ui_font)
        style.map("Treeview", background=[("selected", "lightblue")])

    def apply_dark_mode(self):
        self.root.configure(bg="#1e1e1e")
        self.main_frame.configure(style="Dark.TFrame")
        self.login_frame.configure(style="Dark.TFrame")
        self.tasks_tab.configure(style="Dark.TFrame")
        self.timer_tab.configure(style="Dark.TFrame")
        self.habits_tab.configure(style="Dark.TFrame")
        style = ttk.Style()
        style.configure("Dark.TFrame", background="#1e1e1e")
        style.configure("TLabel", background="#1e1e1e", foreground="white", font=self.ui_font)
        style.configure("TEntry", fieldbackground="#2e2e2e", foreground="white", font=self.ui_font)
        style.configure("TButton", font=self.ui_font)
        style.configure("Treeview", background="#2e2e2e", foreground="white", fieldbackground="#2e2e2e", font=self.ui_font)
        style.configure("Treeview.Heading", font=self.ui_font)
        style.map("Treeview", background=[("selected", "#3e3e3e")])
        self.timer_label.configure(font=self.timer_font)

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductivityApp(root)
    root.mainloop()
