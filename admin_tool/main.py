import customtkinter as ctk
import mysql.connector
from PIL import Image, ImageTk
import os
from dotenv import load_dotenv
import bcrypt
from datetime import datetime
import requests
from io import BytesIO
import tkinter.messagebox as messagebox
from dataclasses import dataclass
from typing import Optional

# Load environment variables
load_dotenv()

@dataclass
class User:
    id: int
    username: str
    email: str
    profile_image: Optional[str]
    created_at: datetime
    comment_count: int
    like_count: int
    photo_count: int

    @property
    def creation_date_formatted(self) -> str:
        return self.created_at.strftime("%Y-%m-%d %H:%M")

@dataclass
class Comment:
    id: int
    content: str
    created_at: datetime
    user_id: int
    photo_id: int
    username: str
    user_profile_image: Optional[str]
    photo_url: str
    photo_title: Optional[str]

    @property
    def creation_date_formatted(self) -> str:
        return self.created_at.strftime("%Y-%m-%d %H:%M")

@dataclass
class Photo:
    id: int
    url: str
    title: Optional[str]
    created_at: datetime
    user_id: int
    username: str
    email: str
    like_count: int
    comment_count: int

    @property
    def creation_date_formatted(self) -> str:
        return self.created_at.strftime("%Y-%m-%d %H:%M")

class Database:
    def __init__(self):
        self.connection = mysql.connector.connect(
            host=os.getenv('DB_HOST'),
            port=int(os.getenv('DB_PORT')),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            database=os.getenv('DB_NAME')
        )
        self.cursor = self.connection.cursor(dictionary=True)

    def get_all_users(self) -> list[User]:
        query = """
        SELECT 
            u.id,
            u.username,
            u.email,
            u.profileImage,
            u.createdAt,
            COUNT(DISTINCT c.id) as comment_count,
            COUNT(DISTINCT l.id) as like_count,
            COUNT(DISTINCT p.id) as photo_count
        FROM User u
        LEFT JOIN Comment c ON c.userId = u.id
        LEFT JOIN `Like` l ON l.userId = u.id
        LEFT JOIN Photo p ON p.userId = u.id
        GROUP BY u.id
        ORDER BY u.createdAt DESC
        """
        self.cursor.execute(query)
        users_data = self.cursor.fetchall()
        
        return [User(
            id=user['id'],
            username=user['username'],
            email=user['email'],
            profile_image=user['profileImage'],
            created_at=user['createdAt'],
            comment_count=user['comment_count'],
            like_count=user['like_count'],
            photo_count=user['photo_count']
        ) for user in users_data]

    def delete_user(self, user_id: int) -> None:
        """Delete a user and all their associated data."""
        try:
            # Start transaction
            self.connection.start_transaction()
            
            # Delete user's likes
            self.cursor.execute("DELETE FROM `Like` WHERE userId = %s", (user_id,))
            
            # Delete user's comments
            self.cursor.execute("DELETE FROM Comment WHERE userId = %s", (user_id,))
            
            # Get user's photos
            self.cursor.execute("SELECT id FROM Photo WHERE userId = %s", (user_id,))
            photos = self.cursor.fetchall()
            
            # Delete likes and comments on user's photos
            for photo in photos:
                self.cursor.execute("DELETE FROM `Like` WHERE photoId = %s", (photo['id'],))
                self.cursor.execute("DELETE FROM Comment WHERE photoId = %s", (photo['id'],))
            
            # Delete user's photos
            self.cursor.execute("DELETE FROM Photo WHERE userId = %s", (user_id,))
            
            # Finally, delete the user
            self.cursor.execute("DELETE FROM User WHERE id = %s", (user_id,))
            
            # Commit transaction
            self.connection.commit()
            
        except Exception as e:
            self.connection.rollback()
            raise e

    def get_latest_photos(self) -> list[Photo]:
        query = """
        SELECT 
            p.id,
            p.url,
            p.title,
            p.createdAt,
            p.userId,
            u.username,
            u.email,
            COUNT(DISTINCT l.id) as like_count,
            COUNT(DISTINCT c.id) as comment_count
        FROM Photo p
        JOIN User u ON p.userId = u.id
        LEFT JOIN `Like` l ON l.photoId = p.id
        LEFT JOIN Comment c ON c.photoId = p.id
        GROUP BY p.id, p.url, p.title, p.createdAt, p.userId, u.username, u.email
        ORDER BY p.createdAt DESC
        """
        self.cursor.execute(query)
        photos_data = self.cursor.fetchall()
        
        return [Photo(
            id=photo['id'],
            url=photo['url'],
            title=photo['title'],
            created_at=photo['createdAt'],
            user_id=photo['userId'],
            username=photo['username'],
            email=photo['email'],
            like_count=photo['like_count'],
            comment_count=photo['comment_count']
        ) for photo in photos_data]

    def delete_photo(self, photo_id: int) -> None:
        """Delete a photo and all its associated data."""
        try:
            # Start transaction
            self.connection.start_transaction()
            
            # Delete likes and comments
            self.cursor.execute("DELETE FROM `Like` WHERE photoId = %s", (photo_id,))
            self.cursor.execute("DELETE FROM Comment WHERE photoId = %s", (photo_id,))
            
            # Delete the photo
            self.cursor.execute("DELETE FROM Photo WHERE id = %s", (photo_id,))
            
            # Commit transaction
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e

    def get_all_comments(self) -> list[Comment]:
        query = """
        SELECT 
            c.id,
            c.content,
            c.createdAt,
            c.userId,
            c.photoId,
            u.username,
            u.profileImage as user_profile_image,
            p.url as photo_url,
            p.title as photo_title
        FROM Comment c
        JOIN User u ON c.userId = u.id
        JOIN Photo p ON c.photoId = p.id
        ORDER BY c.createdAt DESC
        """
        self.cursor.execute(query)
        comments_data = self.cursor.fetchall()
        
        return [Comment(
            id=comment['id'],
            content=comment['content'],
            created_at=comment['createdAt'],
            user_id=comment['userId'],
            photo_id=comment['photoId'],
            username=comment['username'],
            user_profile_image=comment['user_profile_image'],
            photo_url=comment['photo_url'],
            photo_title=comment['photo_title']
        ) for comment in comments_data]

    def delete_comment(self, comment_id: int) -> None:
        """Delete a comment."""
        try:
            self.cursor.execute("DELETE FROM Comment WHERE id = %s", (comment_id,))
            self.connection.commit()
        except Exception as e:
            self.connection.rollback()
            raise e

    def __del__(self):
        self.cursor.close()
        self.connection.close()

class UserCard(ctk.CTkFrame):
    def __init__(self, master, user: User, on_delete_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.user = user
        self.on_delete = on_delete_callback
        
        self.grid_columnconfigure(1, weight=1)
        self.create_widgets()
        
    def create_widgets(self):
        # Profile image
        try:
            if self.user.profile_image:
                response = requests.get(self.user.profile_image)
                img = Image.open(BytesIO(response.content))
                img.thumbnail((100, 100))
                photo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(100, 100))
                img_label = ctk.CTkLabel(self, image=photo_img, text="")
            else:
                img_label = ctk.CTkLabel(self, text="No\nProfile\nPic", width=100, height=100)
        except:
            img_label = ctk.CTkLabel(self, text="No\nProfile\nPic", width=100, height=100)
        
        img_label.grid(row=0, column=0, padx=10, pady=10)

        # User info
        info_frame = ctk.CTkFrame(self)
        info_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        ctk.CTkLabel(info_frame, text=f"Username: {self.user.username}", 
                    font=("Arial", 14, "bold")).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(info_frame, text=f"Email: {self.user.email}").grid(row=1, column=0, sticky="w")
        ctk.CTkLabel(info_frame, text=f"Member since: {self.user.creation_date_formatted}").grid(row=2, column=0, sticky="w")
        ctk.CTkLabel(info_frame, text=f"Activity: {self.user.photo_count} photos • {self.user.comment_count} comments • {self.user.like_count} likes").grid(row=3, column=0, sticky="w")

        # Actions
        actions_frame = ctk.CTkFrame(self)
        actions_frame.grid(row=0, column=2, padx=10, pady=10)

        delete_button = ctk.CTkButton(
            actions_frame, text="Delete Account",
            fg_color="red", hover_color="darkred",
            command=self.delete_user
        )
        delete_button.grid(row=0, column=0, pady=5)
        
    def delete_user(self):
        if messagebox.askokcancel("Delete Account", 
                                f"Are you sure you want to delete the account for {self.user.username}?\n\n"
                                "This will permanently delete:\n"
                                "• All their photos\n"
                                "• All their comments\n"
                                "• All their likes\n"
                                "• Their profile\n\n"
                                "This action cannot be undone!"):
            try:
                self.on_delete(self.user.id)
                messagebox.showinfo("Success", f"Account {self.user.username} has been deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete account: {str(e)}")

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

class CommentCard(ctk.CTkFrame):
    def __init__(self, master, comment: Comment, on_delete_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.comment = comment
        self.on_delete = on_delete_callback
        
        self.grid_columnconfigure(1, weight=1)
        self.create_widgets()
        
    def create_widgets(self):
        # Photo thumbnail
        try:
            response = requests.get(self.comment.photo_url)
            img = Image.open(BytesIO(response.content))
            img.thumbnail((150, 150))
            photo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(150, 150))
            img_label = ctk.CTkLabel(self, image=photo_img, text="")
        except:
            img_label = ctk.CTkLabel(self, text="Photo\nNot Available", width=150, height=150)
        
        img_label.grid(row=0, column=0, padx=10, pady=10)

        # Comment info
        info_frame = ctk.CTkFrame(self)
        info_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # User info with profile pic
        user_frame = ctk.CTkFrame(info_frame)
        user_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        
        try:
            if self.comment.user_profile_image:
                response = requests.get(self.comment.user_profile_image)
                img = Image.open(BytesIO(response.content))
                img.thumbnail((30, 30))
                profile_img = ctk.CTkImage(light_image=img, dark_image=img, size=(30, 30))
                profile_label = ctk.CTkLabel(user_frame, image=profile_img, text="")
            else:
                profile_label = ctk.CTkLabel(user_frame, text="?", width=30, height=30)
        except:
            profile_label = ctk.CTkLabel(user_frame, text="?", width=30, height=30)
        
        profile_label.grid(row=0, column=0, padx=(0, 10))
        
        ctk.CTkLabel(user_frame, text=self.comment.username,
                    font=("Arial", 14, "bold")).grid(row=0, column=1, sticky="w")
        
        # Comment content
        ctk.CTkLabel(info_frame, text=self.comment.content,
                    wraplength=400).grid(row=1, column=0, sticky="w")
        
        # Photo title and date
        photo_info = f"On photo: {self.comment.photo_title or 'Untitled'}"
        ctk.CTkLabel(info_frame, text=photo_info,
                    font=("Arial", 12)).grid(row=2, column=0, sticky="w", pady=(10, 0))
        
        ctk.CTkLabel(info_frame, text=f"Posted on: {self.comment.creation_date_formatted}",
                    font=("Arial", 10)).grid(row=3, column=0, sticky="w")

        # Actions
        actions_frame = ctk.CTkFrame(self)
        actions_frame.grid(row=0, column=2, padx=10, pady=10)

        delete_button = ctk.CTkButton(
            actions_frame, text="Delete Comment",
            fg_color="red", hover_color="darkred",
            command=self.delete_comment
        )
        delete_button.grid(row=0, column=0, pady=5)
        
    def delete_comment(self):
        if messagebox.askokcancel("Delete Comment", 
                                f"Are you sure you want to delete this comment by {self.comment.username}?"):
            try:
                self.on_delete(self.comment.id)
                messagebox.showinfo("Success", "Comment has been deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete comment: {str(e)}")

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

class PhotoCard(ctk.CTkFrame):
    def __init__(self, master, photo: Photo, on_delete_callback, **kwargs):
        super().__init__(master, **kwargs)
        self.photo = photo
        self.on_delete = on_delete_callback
        
        self.grid_columnconfigure(1, weight=1)
        self.create_widgets()
        
    def create_widgets(self):
        # Photo thumbnail
        try:
            response = requests.get(self.photo.url)
            img = Image.open(BytesIO(response.content))
            img.thumbnail((200, 200))
            photo_img = ctk.CTkImage(light_image=img, dark_image=img, size=(200, 200))
            img_label = ctk.CTkLabel(self, image=photo_img, text="")
        except:
            img_label = ctk.CTkLabel(self, text="Photo\nNot Available", width=200, height=200)
        
        img_label.grid(row=0, column=0, padx=10, pady=10)

        # Photo info
        info_frame = ctk.CTkFrame(self)
        info_frame.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")
        
        # Title
        ctk.CTkLabel(info_frame, text=self.photo.title or "Untitled", 
                    font=("Arial", 16, "bold")).grid(row=0, column=0, sticky="w", pady=(0, 5))
        
        # User info
        user_frame = ctk.CTkFrame(info_frame)
        user_frame.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(user_frame, text="Posted by:", 
                    font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=(0, 5))
        ctk.CTkLabel(user_frame, text=self.photo.username,
                    font=("Arial", 12, "bold")).grid(row=0, column=1, sticky="w")
        
        # Stats
        stats_frame = ctk.CTkFrame(info_frame)
        stats_frame.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        
        ctk.CTkLabel(stats_frame, text=f"❤️ {self.photo.like_count} likes",
                    font=("Arial", 12)).grid(row=0, column=0, sticky="w", padx=(0, 15))
        ctk.CTkLabel(stats_frame, text=f"💬 {self.photo.comment_count} comments",
                    font=("Arial", 12)).grid(row=0, column=1, sticky="w")
        
        # Date
        ctk.CTkLabel(info_frame, text=f"Posted on: {self.photo.creation_date_formatted}",
                    font=("Arial", 10)).grid(row=3, column=0, sticky="w")

        # Actions
        actions_frame = ctk.CTkFrame(self)
        actions_frame.grid(row=0, column=2, padx=10, pady=10)

        delete_button = ctk.CTkButton(
            actions_frame, text="Delete Photo",
            fg_color="red", hover_color="darkred",
            command=self.delete_photo
        )
        delete_button.grid(row=0, column=0, pady=5)
        
    def delete_photo(self):
        if messagebox.askokcancel("Delete Photo", 
                                f"Are you sure you want to delete this photo?\n\n"
                                "This will permanently delete:\n"
                                "• The photo\n"
                                "• All its comments\n"
                                "• All its likes\n\n"
                                "This action cannot be undone!"):
            try:
                self.on_delete(self.photo.id)
                messagebox.showinfo("Success", "Photo has been deleted successfully")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to delete photo: {str(e)}")

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

class AdminApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Configure window
        self.title("DevAtHome Admin Tool")
        self.geometry("1200x800")
        
        # Configure grid layout
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Create navigation frame
        self.navigation_frame = ctk.CTkFrame(self, corner_radius=0)
        self.navigation_frame.grid(row=0, column=0, sticky="nsew")
        self.navigation_frame.grid_rowconfigure(5, weight=1)  # Updated to add space for new button

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

        self.film_button = ctk.CTkButton(
            self.navigation_frame, corner_radius=0, height=40,
            border_spacing=10, text="Film Development",
            fg_color="transparent", text_color=("gray10", "gray90"),
            hover_color=("gray70", "gray30"),
            anchor="w",
            command=self.film_button_event
        )
        self.film_button.grid(row=4, column=0, sticky="ew")

        # Create appearance mode menu
        self.appearance_mode_menu = ctk.CTkOptionMenu(
            self.navigation_frame, values=["Light", "Dark", "System"],
            command=self.change_appearance_mode_event
        )
        self.appearance_mode_menu.grid(row=6, column=0, padx=20, pady=20, sticky="s")

        # Create main frame
        self.main_frame = ctk.CTkFrame(self, corner_radius=0)
        self.main_frame.grid(row=0, column=1, sticky="nsew")
        self.main_frame.grid_rowconfigure(0, weight=1)
        self.main_frame.grid_columnconfigure(0, weight=1)

        # Create frames for different sections
        self.user_frame = UserManagementFrame(self.main_frame)
        self.photo_frame = PhotoManagementFrame(self.main_frame)
        self.film_frame = FilmDevelopmentFrame(self.main_frame)
        self.comment_frame = CommentManagementFrame(self.main_frame)

        # Set default frame
        self.select_frame_by_name("user")

    def select_frame_by_name(self, name):
        # Hide all frames
        self.user_frame.grid_remove()
        self.photo_frame.grid_remove()
        self.film_frame.grid_remove()
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
            
        if name == "film":
            self.film_frame.grid(row=0, column=0, sticky="nsew")
            self.film_button.configure(fg_color=("gray75", "gray25"))
        else:
            self.film_button.configure(fg_color="transparent")

        if name == "comment":
            self.comment_frame.grid(row=0, column=0, sticky="nsew")
            self.comment_button.configure(fg_color=("gray75", "gray25"))
        else:
            self.comment_button.configure(fg_color="transparent")

    def user_button_event(self):
        self.select_frame_by_name("user")

    def photo_button_event(self):
        self.select_frame_by_name("photo")

    def film_button_event(self):
        self.select_frame_by_name("film")

    def comment_button_event(self):
        self.select_frame_by_name("comment")

    def change_appearance_mode_event(self, new_appearance_mode):
        ctk.set_appearance_mode(new_appearance_mode)

if __name__ == "__main__":
    app = AdminApp()
    app.mainloop() 