import mysql.connector
import os
from typing import List
from ..models import User, Comment, Photo
from mysql.connector import Error
import bcrypt

class Database:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST'),
                port=int(os.getenv('DB_PORT')),
                user=os.getenv('DB_USER'),
                password=os.getenv('DB_PASSWORD'),
                database=os.getenv('DB_NAME')
            )
            self.cursor = self.connection.cursor(dictionary=True)
        except Error as e:
            print(f"Error connecting to MySQL: {e}")
            raise e

    def get_all_users(self) -> List[User]:
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

    def get_latest_photos(self) -> List[Photo]:
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

    def get_all_comments(self) -> List[Comment]:
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

    def verify_user_login(self, email: str, password: str) -> User:
        try:
            query = "SELECT * FROM User WHERE email = %s"
            self.cursor.execute(query, (email,))
            user_data = self.cursor.fetchone()

            if not user_data:
                raise ValueError("Invalid email or password")

            # Verify password
            if not bcrypt.checkpw(password.encode('utf-8'), user_data['password'].encode('utf-8')):
                raise ValueError("Invalid email or password")

            return User(
                id=user_data['id'],
                username=user_data['username'],
                email=user_data['email'],
                profile_image=user_data['profileImage'],
                role=user_data.get('role', 1)  # Default to regular user if role is not present
            )
        except Error as e:
            print(f"Database error: {e}")
            raise e

    def __del__(self):
        self.cursor.close()
        self.connection.close() 