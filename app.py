import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import subprocess
import json
import os
import atexit
import signal

class ProductivityApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Student Productivity App")
        self.root.geometry("600x500")
        self.is_dark_mode = False
        self.current_user = None
        self.backend_processes = []

        # Register cleanup on exit
        atexit.register(self.cleanup)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)

        # Setup GUI
        self.setup_gui()
        self.apply_light_mode()

    def setup_gui(self):
        # Login Frame
        self.login_frame = ttk.Frame(self.root, padding=10)
        self.login_frame.pack(fill="both", expand=True)

        ttk.Label(self.login_frame, text="Username:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.username_entry = ttk.Entry(self.login_frame)
        self.username_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.login_frame, text="Password:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
        self.password_entry = ttk.Entry(self.login_frame, show="*")
        self.password_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(self.login_frame, text="Register", command=self.register).grid(row=2, column=0, padx=5, pady=5)
        ttk.Button(self.login_frame, text="Login", command=self.login).grid(row=2, column=1, padx=5, pady=5)

        # Task Frame (hidden initially)
        self.task_frame = ttk.Frame(self.root, padding=10)
        ttk.Label(self.task_frame, text="Task:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.task_entry = ttk.Entry(self.task_frame)
        self.task_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        ttk.Button(self.task_frame, text="Add Task", command=self.add_task).grid(row=1, column=0, padx=5, pady=5)
        ttk.Button(self.task_frame, text="Edit Task", command=self.edit_task).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(self.task_frame, text="Delete Task", command=self.delete_task).grid(row=1, column=2, padx=5, pady=5)
        ttk.Button(self.task_frame, text="Change Status", command=self.change_status).grid(row=1, column=3, padx=5, pady=5)

        # Task Table
        self.task_tree = ttk.Treeview(self.task_frame, columns=("ID", "Task", "Status"), show="headings")
        self.task_tree.heading("ID", text="ID")
        self.task_tree.heading("Task", text="Task")
        self.task_tree.heading("Status", text="Status")
        self.task_tree.grid(row=2, column=0, columnspan=4, padx=5, pady=5, sticky="nsew")

        # Theme Toggle
        self.theme_button = ttk.Button(self.task_frame, text="Toggle Dark Mode", command=self.toggle_theme)
        self.theme_button.grid(row=3, column=3, padx=5, pady=5, sticky="e")

        self.task_frame.pack_forget()  # Hide initially
        self.task_frame.grid_columnconfigure(1, weight=1)

    def call_backend(self, args):
        try:
            process = subprocess.run(
                ["java", "-cp", ".", "Backend"] + args,
                capture_output=True, text=True, cwd=os.path.dirname(os.path.abspath(__file__)),
                timeout=5  # Prevent hanging
            )
            return process.stdout.strip(), process.stderr.strip()
        except subprocess.TimeoutExpired:
            return "", "Backend operation timed out"
        except Exception as e:
            return "", str(e)

    def cleanup(self):
        # Ensure all backend processes are terminated
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
            self.task_frame.pack(fill="both", expand=True)
            self.load_tasks()
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
        new_task = simpledialog.askstring("Edit Task", "New task description:", initialvalue=self.task_tree.item(selected)["values"][1])
        if new_task:
            stdout, stderr = self.call_backend(["edit", self.current_user, str(task_id), new_task])
            if stderr:
                messagebox.showerror("Error", stderr)
            else:
                self.load_tasks()

    def change_status(self):
        selected = self.task_tree.selection()
        if not selected:
            messagebox.showerror("Error", "Please select a task to change status")
            return
        task_id = self.task_tree.item(selected)["values"][0]
        status_dialog = tk.Toplevel(self.root)
        status_dialog.title("Change Task Status")
        status_dialog.geometry("200x100")
        status_dialog.transient(self.root)
        status_dialog.grab_set()

        ttk.Label(status_dialog, text="Select Status:").pack(pady=5)
        status_var = tk.StringVar(value=self.task_tree.item(selected)["values"][2])
        status_combobox = ttk.Combobox(status_dialog, textvariable=status_var, values=["Pending", "Completed"], state="readonly")
        status_combobox.pack(pady=5)

        def submit_status():
            new_status = status_var.get()
            stdout, stderr = self.call_backend(["change_status", self.current_user, str(task_id), new_status])
            if stderr:
                messagebox.showerror("Error", stderr)
            else:
                self.load_tasks()
                status_dialog.destroy()

        ttk.Button(status_dialog, text="Submit", command=submit_status).pack(pady=5)

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
        stdout, stderr = self.call_backend(["list", self.current_user])
        if stderr:
            messagebox.showerror("Error", stderr)
        else:
            try:
                tasks = json.loads(stdout) if stdout else []
                for task in tasks:
                    self.task_tree.insert("", tk.END, values=(task["id"], task["description"], task["status"]))
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
        self.login_frame.configure(style="Light.TFrame")
        self.task_frame.configure(style="Light.TFrame")
        self.theme_button.configure(text="Toggle Dark Mode")
        style = ttk.Style()
        style.configure("Light.TFrame", background="white")
        style.configure("TLabel", background="white", foreground="black")
        style.configure("TEntry", fieldbackground="white", foreground="black")
        style.configure("Treeview", background="white", foreground="black", fieldbackground="white")
        style.map("Treeview", background=[("selected", "lightblue")])

    def apply_dark_mode(self):
        self.root.configure(bg="#1e1e1e")
        self.login_frame.configure(style="Dark.TFrame")
        self.task_frame.configure(style="Dark.TFrame")
        self.theme_button.configure(text="Toggle Light Mode")
        style = ttk.Style()
        style.configure("Dark.TFrame", background="#1e1e1e")
        style.configure("TLabel", background="#1e1e1e", foreground="white")
        style.configure("TEntry", fieldbackground="#2e2e2e", foreground="white")
        style.configure("Treeview", background="#2e2e2e", foreground="white", fieldbackground="#2e2e2e")
        style.map("Treeview", background=[("selected", "#3e3e3e")])

if __name__ == "__main__":
    root = tk.Tk()
    app = ProductivityApp(root)
    root.mainloop()
