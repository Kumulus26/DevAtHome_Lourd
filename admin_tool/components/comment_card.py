import customtkinter as ctk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import tkinter.messagebox as messagebox

from ..models import Comment

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