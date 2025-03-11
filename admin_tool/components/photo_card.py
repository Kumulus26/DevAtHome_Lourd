import customtkinter as ctk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import tkinter.messagebox as messagebox

from ..models import Photo

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