import customtkinter as ctk
from dotenv import load_dotenv

from .components import (
    UserManagementFrame,
    PhotoManagementFrame,
    CommentManagementFrame,
    LoginFrame
)

# Load environment variables
load_dotenv()

class AdminApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("DevAtHome Admin Tool")
        self.geometry("1200x800")
        
        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # Create login frame
        self.login_frame = LoginFrame(self, self.on_successful_login)
        self.login_frame.grid(row=0, column=0, sticky="nsew")

        # Initialize admin interface (hidden initially)
        self.initialize_admin_interface()
        self.hide_admin_interface()

    def initialize_admin_interface(self):
        # Configure grid layout for admin interface
        self.grid_columnconfigure(1, weight=1)

        # Create navigation frame
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(4, weight=1)

        self.navigation_frame_label = ctk.CTkLabel(
            self.navigation_frame, text="DevAtHome Admin",
            compound="left", font=ctk.CTkFont(size=15, weight="bold")
        )
        self.navigation_frame_label.grid(row=0, column=0, padx=20, pady=20)

        # Create navigation buttons
        self.user_button = ctk.CTkButton(
            self.navigation_frame, corner_radius=0, height=40,
            border_spacing=10, text="User Management",
            fg_color="transparent", text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            command=self.user_button_event
        )
        self.user_button.grid(row=1, column=0, sticky="ew")

        self.photo_button = ctk.CTkButton(
            self.navigation_frame, corner_radius=0, height=40,
            border_spacing=10, text="Photo Management",
            fg_color="transparent", text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            command=self.photo_button_event
        )
        self.photo_button.grid(row=2, column=0, sticky="ew")

        self.comment_button = ctk.CTkButton(
            self.navigation_frame, corner_radius=0, height=40,
            border_spacing=10, text="Comment Management",
            fg_color="transparent", text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            command=self.comment_button_event
        )
        self.comment_button.grid(row=3, column=0, sticky="ew")

        # Create appearance mode menu
        self.appearance_mode_menu = ctk.CTkOptionMenu(
            self.navigation_frame, values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event
        )
        self.appearance_mode_menu.grid(row=5, column=0, padx=20, pady=20, sticky="s")

        # Create main frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Create frames for different sections
        self.user_frame = UserManagementFrame(self.main_frame)
        self.photo_frame = PhotoManagementFrame(self.main_frame)
        self.comment_frame = CommentManagementFrame(self.main_frame)

        # Set default frame
        self.select_frame_by_name("user")

    def hide_admin_interface(self):
        if hasattr(self, 'navigation_frame'):
            self.navigation_frame.grid_remove()
        if hasattr(self, 'main_frame'):
            self.main_frame.grid_remove()

    def show_admin_interface(self):
        self.login_frame.grid_remove()
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.select_frame_by_name("user")

    def on_successful_login(self):
        self.show_admin_interface()

    def select_frame_by_name(self, name):
        # Hide all frames
        self.user_frame.grid_remove()
        self.photo_frame.grid_remove()
        self.comment_frame.grid_remove()

        # Show selected frame
        if name == "user":
            self.user_frame.grid(row=0, column=0, sticky="nsew")
            self.user_button.configure(fg_color=("gray75", "gray25"))
        else:
            self.user_button.configure(fg_color="transparent")
        
        if name == "photo":
            self.photo_frame.grid(row=0, column=0, sticky="nsew")
            self.photo_button.configure(fg_color=("gray75", "gray25"))
        else:
            self.photo_button.configure(fg_color="transparent")

        if name == "comment":
            self.comment_frame.grid(row=0, column=0, sticky="nsew")
            self.comment_button.configure(fg_color=("gray75", "gray25"))
        else:
            self.comment_button.configure(fg_color="transparent")

    def user_button_event(self):
        self.select_frame_by_name("user")

    def photo_button_event(self):
        self.select_frame_by_name("photo")

    def comment_button_event(self):
        self.select_frame_by_name("comment")

    def change_appearance_mode_event(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)

if __name__ == "__main__":
    app = AdminApp()
    app.mainloop() 