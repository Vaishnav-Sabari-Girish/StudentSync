import customtkinter as ctk
from tkinter import messagebox, simpledialog
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
        self.root.geometry("800x650")  # Increased window size to accommodate larger fonts
        self.is_dark_mode = False
        self.current_user = None
        self.backend_processes = []
        self.timer_running = False
        self.timer_seconds = 25 * 60  # Default to 25 minutes
        self.pomodoro_count = 0
        self.task_checkboxes = {}  # Store checkbox states for tasks
        self.habit_checkboxes = {}  # Store checkbox states for habits

        # Register cleanup on exit
        atexit.register(self.cleanup)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Setup GUI
        self.setup_gui()
        self.apply_light_mode()

    def setup_gui(self):
        # Main container
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        # Login Frame
        self.login_frame = ctk.CTkFrame(self.main_frame)
        self.login_frame.pack(fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(self.login_frame, text="Username:", font=ctk.CTkFont(size=20)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        self.username_entry = ctk.CTkEntry(self.login_frame, font=ctk.CTkFont(size=18), height=40)
        self.username_entry.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(self.login_frame, text="Password:", font=ctk.CTkFont(size=20)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.password_entry = ctk.CTkEntry(self.login_frame, show="*", font=ctk.CTkFont(size=18), height=40)
        self.password_entry.grid(row=1, column=1, padx=10, pady=10)

        ctk.CTkButton(self.login_frame, text="Register", command=self.register, font=ctk.CTkFont(size=18), height=45).grid(row=2, column=0, padx=10, pady=10)
        ctk.CTkButton(self.login_frame, text="Login", command=self.login, font=ctk.CTkFont(size=18), height=45).grid(row=2, column=1, padx=10, pady=10)

        # Tabview for tabs (hidden initially)
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.configure(segmented_button_fg_color=("gray75", "gray25"))
        self.tasks_tab = self.tabview.add("Tasks")
        self.timer_tab = self.tabview.add("Focus Timer")
        self.habits_tab = self.tabview.add("Habit Planner")
        self.tabview.pack_forget()

        # Tasks Tab
        self.task_progress_label = ctk.CTkLabel(self.tasks_tab, text="Progress: 0%", font=ctk.CTkFont(size=18, weight="bold"))
        self.task_progress_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="w")
        self.task_progress = ctk.CTkProgressBar(self.tasks_tab, width=350, height=20)
        self.task_progress.grid(row=0, column=3, padx=10, pady=10, sticky="e")
        self.task_progress.set(0)

        ctk.CTkLabel(self.tasks_tab, text="Task:", font=ctk.CTkFont(size=18)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.task_entry = ctk.CTkEntry(self.tasks_tab, font=ctk.CTkFont(size=16), height=40)
        self.task_entry.grid(row=1, column=1, columnspan=2, padx=10, pady=10, sticky="ew")

        ctk.CTkButton(self.tasks_tab, text="Add Task", command=self.add_task, font=ctk.CTkFont(size=16), height=40).grid(row=2, column=0, padx=10, pady=10)
        ctk.CTkButton(self.tasks_tab, text="Edit Task", command=self.edit_task, font=ctk.CTkFont(size=16), height=40).grid(row=2, column=1, padx=10, pady=10)
        ctk.CTkButton(self.tasks_tab, text="Delete Task", command=self.delete_task, font=ctk.CTkFont(size=16), height=40).grid(row=2, column=2, padx=10, pady=10)

        # Create task list using CTkScrollableFrame
        self.task_list_frame = ctk.CTkScrollableFrame(self.tasks_tab, width=650, height=250)
        self.task_list_frame.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")
        
        self.tasks_tab.grid_columnconfigure(1, weight=1)

        # Focus Timer Tab
        self.timer_progress_label = ctk.CTkLabel(self.timer_tab, text="Progress: 0%", font=ctk.CTkFont(size=18, weight="bold"))
        self.timer_progress_label.pack(pady=10)
        self.timer_progress = ctk.CTkProgressBar(self.timer_tab, width=400, height=25)
        self.timer_progress.pack(pady=10)
        self.timer_progress.set(0)

        self.timer_label = ctk.CTkLabel(self.timer_tab, text="25:00", font=ctk.CTkFont(size=48, weight="bold"))
        self.timer_label.pack(pady=25)

        ctk.CTkButton(self.timer_tab, text="Start", command=self.start_timer, font=ctk.CTkFont(size=18), height=45, width=120).pack(pady=8)
        ctk.CTkButton(self.timer_tab, text="Pause", command=self.pause_timer, font=ctk.CTkFont(size=18), height=45, width=120).pack(pady=8)
        ctk.CTkButton(self.timer_tab, text="Reset", command=self.reset_timer, font=ctk.CTkFont(size=18), height=45, width=120).pack(pady=8)

        self.pomodoro_status = ctk.CTkLabel(self.timer_tab, text="Work Session (Pomodoro #1)", font=ctk.CTkFont(size=18, weight="bold"))
        self.pomodoro_status.pack(pady=15)

        # Habit Planner Tab
        self.habit_progress_label = ctk.CTkLabel(self.habits_tab, text="Progress: 0%", font=ctk.CTkFont(size=18, weight="bold"))
        self.habit_progress_label.grid(row=0, column=0, columnspan=3, padx=10, pady=10, sticky="w")
        self.habit_progress = ctk.CTkProgressBar(self.habits_tab, width=350, height=20)
        self.habit_progress.grid(row=0, column=3, padx=10, pady=10, sticky="e")
        self.habit_progress.set(0)

        ctk.CTkLabel(self.habits_tab, text="Routine:", font=ctk.CTkFont(size=18)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        self.habit_entry = ctk.CTkEntry(self.habits_tab, font=ctk.CTkFont(size=16), height=40)
        self.habit_entry.grid(row=1, column=1, padx=10, pady=10, sticky="ew")

        ctk.CTkLabel(self.habits_tab, text="Time (min):", font=ctk.CTkFont(size=18)).grid(row=1, column=2, padx=10, pady=10, sticky="e")
        self.habit_time = ctk.CTkEntry(self.habits_tab, width=80, font=ctk.CTkFont(size=16), height=40)
        self.habit_time.grid(row=1, column=3, padx=10, pady=10)

        ctk.CTkButton(self.habits_tab, text="Add Routine", command=self.add_habit, font=ctk.CTkFont(size=16), height=40).grid(row=2, column=0, padx=10, pady=10)
        ctk.CTkButton(self.habits_tab, text="Edit Routine", command=self.edit_habit, font=ctk.CTkFont(size=16), height=40).grid(row=2, column=1, padx=10, pady=10)
        ctk.CTkButton(self.habits_tab, text="Delete Routine", command=self.delete_habit, font=ctk.CTkFont(size=16), height=40).grid(row=2, column=2, padx=10, pady=10)

        # Create habit list using CTkScrollableFrame
        self.habit_list_frame = ctk.CTkScrollableFrame(self.habits_tab, width=650, height=250)
        self.habit_list_frame.grid(row=3, column=0, columnspan=4, padx=10, pady=10, sticky="nsew")

        self.habits_tab.grid_columnconfigure(1, weight=1)

        # Theme Toggle
        self.theme_button = ctk.CTkButton(self.main_frame, text="Toggle Dark Mode", command=self.toggle_theme, font=ctk.CTkFont(size=16), height=40)
        self.theme_button.pack(pady=10, anchor="e")

        # Store task and habit widgets
        self.task_widgets = []
        self.habit_widgets = []

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
            self.tabview.pack(fill="both", expand=True)
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
            self.task_entry.delete(0, "end")
            self.load_tasks()

    def edit_task(self):
        if not hasattr(self, 'selected_task_id') or self.selected_task_id is None:
            messagebox.showerror("Error", "Please select a task to edit")
            return
        new_task = simpledialog.askstring("Edit Task", "New task description:", parent=self.root)
        if new_task:
            stdout, stderr = self.call_backend(["edit", self.current_user, str(self.selected_task_id), new_task])
            if stderr:
                messagebox.showerror("Error", stderr)
            else:
                self.load_tasks()

    def delete_task(self):
        if not hasattr(self, 'selected_task_id') or self.selected_task_id is None:
            messagebox.showerror("Error", "Please select a task to delete")
            return
        stdout, stderr = self.call_backend(["delete", self.current_user, str(self.selected_task_id)])
        if stderr:
            messagebox.showerror("Error", stderr)
        else:
            self.load_tasks()

    def select_task(self, task_id):
        self.selected_task_id = task_id
        # Update visual selection
        for widget_set in self.task_widgets:
            if widget_set["id"] == task_id:
                widget_set["frame"].configure(fg_color=("lightblue", "darkblue"))
            else:
                widget_set["frame"].configure(fg_color="transparent")

    def toggle_task_completion(self, task_id):
        current_state = self.task_checkboxes.get(task_id, False)
        new_state = not current_state
        stdout, stderr = self.call_backend(["change_status", self.current_user, str(task_id), str(new_state).lower()])
        if stderr:
            messagebox.showerror("Error", stderr)
        else:
            self.load_tasks()

    def load_tasks(self):
        # Clear existing widgets
        for widget_set in self.task_widgets:
            widget_set["frame"].destroy()
        self.task_widgets.clear()
        self.task_checkboxes.clear()
        
        stdout, stderr = self.call_backend(["list", self.current_user])
        if stderr:
            messagebox.showerror("Error", stderr)
        else:
            try:
                tasks = json.loads(stdout) if stdout else []
                completed_count = sum(1 for task in tasks if task["completed"])
                total_count = len(tasks)
                progress = (completed_count / total_count) if total_count > 0 else 0
                self.task_progress.set(progress)
                self.task_progress_label.configure(text=f"Progress: {int(progress * 100)}%")
                
                for i, task in enumerate(tasks):
                    task_id = task["id"]
                    task_desc = task["description"]
                    task_completed = task["completed"]
                    self.task_checkboxes[task_id] = task_completed
                    
                    # Create frame for each task
                    task_frame = ctk.CTkFrame(self.task_list_frame, height=60)
                    task_frame.pack(fill="x", padx=8, pady=5)
                    
                    # Task ID label
                    id_label = ctk.CTkLabel(task_frame, text=str(task_id), width=60, font=ctk.CTkFont(size=16, weight="bold"))
                    id_label.pack(side="left", padx=10, pady=10)
                    
                    # Task description label
                    desc_label = ctk.CTkLabel(task_frame, text=task_desc, width=400, anchor="w", font=ctk.CTkFont(size=16))
                    desc_label.pack(side="left", padx=10, pady=10)
                    
                    # Checkbox
                    checkbox = ctk.CTkCheckBox(task_frame, text="", width=30, height=30,
                                             command=lambda tid=task_id: self.toggle_task_completion(tid))
                    if task_completed:
                        checkbox.select()
                    checkbox.pack(side="right", padx=15, pady=10)
                    
                    # Make frame and labels clickable for selection
                    def make_clickable(widget, tid):
                        widget.bind("<Button-1>", lambda e: self.select_task(tid))
                    
                    make_clickable(task_frame, task_id)
                    make_clickable(id_label, task_id)
                    make_clickable(desc_label, task_id)
                    
                    widget_set = {
                        "id": task_id,
                        "frame": task_frame,
                        "id_label": id_label,
                        "desc_label": desc_label,
                        "checkbox": checkbox
                    }
                    self.task_widgets.append(widget_set)
                    
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
        self.timer_progress.set(0)
        self.timer_progress_label.configure(text="Progress: 0%")
        if self.pomodoro_count % 8 == 7:
            self.pomodoro_count = 0
            self.pomodoro_status.configure(text="Work Session (Pomodoro #1)")
        else:
            self.pomodoro_status.configure(text=f"{'Work Session' if self.pomodoro_count % 2 == 0 else 'Break'} (Pomodoro #{(self.pomodoro_count // 2) + 1})")

    def update_timer(self):
        if self.timer_running and self.timer_seconds > 0:
            self.timer_seconds -= 1
            self.update_timer_display()
            total_seconds = 25 * 60 if self.pomodoro_count % 2 == 0 else 5 * 60
            progress = ((total_seconds - self.timer_seconds) / total_seconds)
            self.timer_progress.set(progress)
            self.timer_progress_label.configure(text=f"Progress: {int(progress * 100)}%")
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
            self.timer_progress.set(1.0)
            self.timer_progress_label.configure(text="Progress: 100%")
            self.pomodoro_status.configure(text=f"{'Work Session' if self.pomodoro_count % 2 == 0 else 'Break'} (Pomodoro #{(self.pomodoro_count // 2) + 1})")

    def update_timer_display(self):
        minutes = self.timer_seconds // 60
        seconds = self.timer_seconds % 60
        self.timer_label.configure(text=f"{minutes:02d}:{seconds:02d}")

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
            self.habit_entry.delete(0, "end")
            self.habit_time.delete(0, "end")
            self.load_habits()

    def edit_habit(self):
        if not hasattr(self, 'selected_habit_id') or self.selected_habit_id is None:
            messagebox.showerror("Error", "Please select a routine to edit")
            return
        
        # Find current habit data
        current_routine = ""
        current_time = ""
        for widget_set in self.habit_widgets:
            if widget_set["id"] == self.selected_habit_id:
                current_routine = widget_set["routine_text"]
                current_time = widget_set["time_text"]
                break

        edit_dialog = ctk.CTkToplevel(self.root)
        edit_dialog.title("Edit Routine")
        edit_dialog.geometry("400x200")
        edit_dialog.transient(self.root)
        
        # Wait for the window to be created and visible before grabbing
        edit_dialog.update_idletasks()  # Ensure window is fully created
        edit_dialog.after(10, lambda: edit_dialog.grab_set())  # Delay grab_set slightly

        ctk.CTkLabel(edit_dialog, text="Routine:", font=ctk.CTkFont(size=18)).grid(row=0, column=0, padx=10, pady=10, sticky="e")
        routine_entry = ctk.CTkEntry(edit_dialog, font=ctk.CTkFont(size=16), height=40)
        routine_entry.insert(0, current_routine)
        routine_entry.grid(row=0, column=1, padx=10, pady=10)

        ctk.CTkLabel(edit_dialog, text="Time (min):", font=ctk.CTkFont(size=18)).grid(row=1, column=0, padx=10, pady=10, sticky="e")
        time_entry = ctk.CTkEntry(edit_dialog, font=ctk.CTkFont(size=16), height=40)
        time_entry.insert(0, str(current_time))
        time_entry.grid(row=1, column=1, padx=10, pady=10)

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
            stdout, stderr = self.call_backend(["edit_habit", self.current_user, str(self.selected_habit_id), new_routine, str(new_time)])
            if stderr:
                messagebox.showerror("Error", stderr)
            else:
                self.load_habits()
            edit_dialog.destroy()

        ctk.CTkButton(edit_dialog, text="Submit", command=submit_edit, font=ctk.CTkFont(size=16), height=40).grid(row=2, column=0, columnspan=2, pady=15)

    def delete_habit(self):
        if not hasattr(self, 'selected_habit_id') or self.selected_habit_id is None:
            messagebox.showerror("Error", "Please select a routine to delete")
            return
        stdout, stderr = self.call_backend(["delete_habit", self.current_user, str(self.selected_habit_id)])
        if stderr:
            messagebox.showerror("Error", stderr)
        else:
            self.load_habits()

    def select_habit(self, habit_id):
        self.selected_habit_id = habit_id
        # Update visual selection
        for widget_set in self.habit_widgets:
            if widget_set["id"] == habit_id:
                widget_set["frame"].configure(fg_color=("lightblue", "darkblue"))
            else:
                widget_set["frame"].configure(fg_color="transparent")

    def toggle_habit_completion(self, habit_id):
        current_state = self.habit_checkboxes.get(habit_id, False)
        new_state = not current_state
        stdout, stderr = self.call_backend(["change_habit_status", self.current_user, str(habit_id), str(new_state).lower()])
        if stderr:
            messagebox.showerror("Error", stderr)
        else:
            self.load_habits()

    def load_habits(self):
        # Clear existing widgets
        for widget_set in self.habit_widgets:
            widget_set["frame"].destroy()
        self.habit_widgets.clear()
        self.habit_checkboxes.clear()
        
        stdout, stderr = self.call_backend(["list_habits", self.current_user])
        if stderr:
            messagebox.showerror("Error", stderr)
        else:
            try:
                habits = json.loads(stdout) if stdout else []
                completed_count = sum(1 for habit in habits if habit["completed"])
                total_count = len(habits)
                progress = (completed_count / total_count) if total_count > 0 else 0
                self.habit_progress.set(progress)
                self.habit_progress_label.configure(text=f"Progress: {int(progress * 100)}%")
                
                for habit in habits:
                    habit_id = habit["id"]
                    habit_routine = habit["routine"]
                    habit_time = habit["time"]
                    habit_completed = habit["completed"]
                    self.habit_checkboxes[habit_id] = habit_completed
                    
                    # Create frame for each habit
                    habit_frame = ctk.CTkFrame(self.habit_list_frame, height=60)
                    habit_frame.pack(fill="x", padx=8, pady=5)
                    
                    # Habit ID label
                    id_label = ctk.CTkLabel(habit_frame, text=str(habit_id), width=60, font=ctk.CTkFont(size=16, weight="bold"))
                    id_label.pack(side="left", padx=10, pady=10)
                    
                    # Habit routine label
                    routine_label = ctk.CTkLabel(habit_frame, text=habit_routine, width=250, anchor="w", font=ctk.CTkFont(size=16))
                    routine_label.pack(side="left", padx=10, pady=10)
                    
                    # Habit time label
                    time_label = ctk.CTkLabel(habit_frame, text=f"{habit_time} min", width=120, font=ctk.CTkFont(size=16))
                    time_label.pack(side="left", padx=10, pady=10)
                    
                    # Checkbox
                    checkbox = ctk.CTkCheckBox(habit_frame, text="", width=30, height=30,
                                             command=lambda hid=habit_id: self.toggle_habit_completion(hid))
                    if habit_completed:
                        checkbox.select()
                    checkbox.pack(side="right", padx=15, pady=10)
                    
                    # Make frame and labels clickable for selection
                    def make_clickable(widget, hid):
                        widget.bind("<Button-1>", lambda e: self.select_habit(hid))
                    
                    make_clickable(habit_frame, habit_id)
                    make_clickable(id_label, habit_id)
                    make_clickable(routine_label, habit_id)
                    make_clickable(time_label, habit_id)
                    
                    widget_set = {
                        "id": habit_id,
                        "frame": habit_frame,
                        "id_label": id_label,
                        "routine_label": routine_label,
                        "time_label": time_label,
                        "checkbox": checkbox,
                        "routine_text": habit_routine,
                        "time_text": habit_time
                    }
                    self.habit_widgets.append(widget_set)
                    
            except json.JSONDecodeError:
                messagebox.showerror("Error", "Invalid response from backend")

    def toggle_theme(self):
        self.is_dark_mode = not self.is_dark_mode
        if self.is_dark_mode:
            self.apply_dark_mode()
        else:
            self.apply_light_mode()

    def apply_light_mode(self):
        ctk.set_appearance_mode("light")

    def apply_dark_mode(self):
        ctk.set_appearance_mode("dark")

if __name__ == "__main__":
    ctk.set_appearance_mode("light")  # Default to light mode
    ctk.set_default_color_theme("blue")  # Default color theme
    
    root = ctk.CTk()
    app = ProductivityApp(root)
    root.mainloop()
