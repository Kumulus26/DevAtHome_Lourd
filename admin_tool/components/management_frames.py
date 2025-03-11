import customtkinter as ctk
from ..database import Database
from .user_card import UserCard
from .photo_card import PhotoCard
from .comment_card import CommentCard

class UserManagementFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.db = Database()

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Add title
        self.title = ctk.CTkLabel(
            self, text="User Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title.grid(row=0, column=0, padx=20, pady=(20,10))

        # Create scrollable frame for user cards
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Load and display users
        self.load_users()

    def load_users(self):
        users = self.db.get_all_users()
        
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Create user cards
        for i, user in enumerate(users):
            user_card = UserCard(
                self.scrollable_frame,
                user=user,
                on_delete_callback=self.delete_user
            )
            user_card.grid(row=i, column=0, pady=(0,10), sticky="ew")

    def delete_user(self, user_id: int):
        try:
            self.db.delete_user(user_id)
            self.load_users()  # Refresh the list
        except Exception as e:
            raise e

class CommentManagementFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.db = Database()

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Add title
        self.title = ctk.CTkLabel(
            self, text="Comment Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title.grid(row=0, column=0, padx=20, pady=(20,10))

        # Create scrollable frame for comment cards
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Load and display comments
        self.load_comments()

    def load_comments(self):
        comments = self.db.get_all_comments()
        
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Create comment cards
        for i, comment in enumerate(comments):
            comment_card = CommentCard(
                self.scrollable_frame,
                comment=comment,
                on_delete_callback=self.delete_comment
            )
            comment_card.grid(row=i, column=0, pady=(0,10), sticky="ew")

    def delete_comment(self, comment_id: int):
        try:
            self.db.delete_comment(comment_id)
            self.load_comments()  # Refresh the list
        except Exception as e:
            raise e

class PhotoManagementFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)
        self.db = Database()

        # Configure grid
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Add title
        self.title = ctk.CTkLabel(
            self, text="Photo Management",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title.grid(row=0, column=0, padx=20, pady=(20,10))

        # Create scrollable frame for photo cards
        self.scrollable_frame = ctk.CTkScrollableFrame(self)
        self.scrollable_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.scrollable_frame.grid_columnconfigure(0, weight=1)

        # Load and display photos
        self.load_photos()

    def load_photos(self):
        photos = self.db.get_latest_photos()
        
        # Clear existing widgets
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()

        # Create photo cards
        for i, photo in enumerate(photos):
            photo_card = PhotoCard(
                self.scrollable_frame,
                photo=photo,
                on_delete_callback=self.delete_photo
            )
            photo_card.grid(row=i, column=0, pady=(0,20), sticky="ew")

    def delete_photo(self, photo_id: int):
        try:
            self.db.delete_photo(photo_id)
            self.load_photos()  # Refresh the list
        except Exception as e:
            raise e

class FilmDevelopmentFrame(ctk.CTkFrame):
    def __init__(self, master, **kwargs):
        super().__init__(master, **kwargs)

        # Configure grid
        self.grid_columnconfigure(0, weight=1)

        # Add title
        self.title = ctk.CTkLabel(
            self, text="Film Development Management",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        self.title.grid(row=0, column=0, padx=20, pady=20) 