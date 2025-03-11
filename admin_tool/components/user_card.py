import customtkinter as ctk
from PIL import Image, ImageTk
import requests
from io import BytesIO
import tkinter.messagebox as messagebox

from ..models import User

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