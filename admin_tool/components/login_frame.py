import customtkinter as ctk
from ..database import Database
import tkinter.messagebox as messagebox

class LoginFrame(ctk.CTkFrame):
    def __init__(self, master, on_successful_login, **kwargs):
        super().__init__(master, **kwargs)
        self.db = Database()
        self.on_successful_login = on_successful_login

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(3, weight=1)

        # Add title
        self.title = ctk.CTkLabel(
            self, text="Admin Login",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title.grid(row=0, column=0, padx=20, pady=(40, 20))

        # Create login form
        self.email_entry = ctk.CTkEntry(
            self, placeholder_text="Email",
            width=300
        )
        self.email_entry.grid(row=1, column=0, padx=20, pady=(0, 10))

        self.password_entry = ctk.CTkEntry(
            self, placeholder_text="Password",
            show="*", width=300
        )
        self.password_entry.grid(row=2, column=0, padx=20, pady=(0, 20))

        self.login_button = ctk.CTkButton(
            self, text="Login",
            command=self.login,
            width=300
        )
        self.login_button.grid(row=3, column=0, padx=20, pady=(0, 20))

    def login(self):
        email = self.email_entry.get()
        password = self.password_entry.get()

        if not email or not password:
            messagebox.showerror("Error", "Please fill in all fields")
            return

        try:
            user = self.db.verify_user_login(email, password)
            if user and user.role == 2:  # Admin role
                self.on_successful_login()
            else:
                messagebox.showerror("Error", "Access denied. Admin privileges required.")
        except Exception as e:
            messagebox.showerror("Error", str(e)) 