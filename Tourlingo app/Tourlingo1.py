from googletrans import Translator
import mysql.connector
from mysql.connector import Error

class LanguageTranslatorAPP:
    def __init__(self):
        self.translator = Translator()
        self.db_connection = self.initialize_database()
        self.current_user = None  # Keep track of the current user
        self.current_user_id = None  # Keep track of the current user's ID

    # Initialization method to connect to the database
    def initialize_database(self):
        try:
            connection = mysql.connector.connect(
                host="localhost",
                user="kabisa",
                password="Argentina@10",
                database="tourlingodbs"
            )
            return connection
        except Error as e:
            print(f"Error connecting to the database: {e}")
            raise

    # Function to print visual borders
    def print_visual_border(self):
        print("------------------------------")

    # Method to create a new user and insert into both tables
    def create_user(self, username, password):
        try:
            cursor = self.db_connection.cursor()

            # Insert into data table
            query_data = "INSERT INTO data (username, password) VALUES (%s, %s)"
            values_data = (username, password)
            cursor.execute(query_data, values_data)
            self.db_connection.commit()

            # Get the last inserted ID (auto-incremented primary key)
            user_id = cursor.lastrowid

            # Insert into user_progress table with the same ID
            query_progress = "INSERT INTO user_progress (id, translations_completed) VALUES (%s, 0)"
            values_progress = (user_id,)
            cursor.execute(query_progress, values_progress)
            self.db_connection.commit()

            # Consume any pending results
            cursor.fetchall()

            cursor.close()
            self.print_visual_border()
            print("User created successfully!")
            self.print_visual_border()
        except Error as e:
            print(f"Error creating user: {e}")

    # Method to authenticate a user
    def authenticate_user(self, username, password):
        try:
            cursor = self.db_connection.cursor()
            query = "SELECT id FROM data WHERE username=%s AND password=%s"
            values = (username, password)
            cursor.execute(query, values)
            user_data = cursor.fetchone()
            cursor.close()
            return user_data[0] if user_data else None
        except Error as e:
            print(f"Error authenticating user: {e}")
            return None

    # Method to update translations completed for a user
    def update_translations_completed(self, user_id):
        try:
            cursor = self.db_connection.cursor()
            query_update = "UPDATE user_progress SET translations_completed = translations_completed + 1 WHERE id = %s"
            values_update = (user_id,)
            cursor.execute(query_update, values_update)
            self.db_connection.commit()
            cursor.close()
            self.print_visual_border()
            print("Translations completed!")
            self.print_visual_border()
        except Error as e:
            print(f"Error updating translations completed: {e}")

    # Method to get user's progress
    def get_user_progress(self, user_id):
        try:
            cursor = self.db_connection.cursor()
            query_select = "SELECT translations_completed FROM user_progress WHERE id = %s"
            values_select = (user_id,)
            cursor.execute(query_select, values_select)
            progress_row = cursor.fetchone()

            if progress_row is not None:
                current_translations_completed = progress_row[0]
                cursor.close()
                return current_translations_completed
            else:
                self.print_visual_border()
                print("No progress found.")
                self.print_visual_border()
                cursor.close()
                return 0  # Default progress assumed to be 0 if no data found
        except Error as e:
            print(f"Error getting user progress: {e}")
            return None

    # Method to log in a user
    def login(self):
        username_to_authenticate = input("Enter your username for authentication: ")
        password_to_authenticate = input("Enter your password for authentication: ")
        authenticated_user_id = self.authenticate_user(username_to_authenticate, password_to_authenticate)

        if authenticated_user_id is not None:
            self.print_visual_border()
            print("Login successful!")
            self.print_visual_border()
            self.current_user = username_to_authenticate
            self.current_user_id = authenticated_user_id
        else:
            self.print_visual_border()
            print("Authentication failed. Check your credentials.")
            self.print_visual_border()

    # Method to translate text for a logged-in user
    def translate_text(self):
        if not self.current_user:
            self.print_visual_border()
            print("You need to log in first.")
            self.print_visual_border()
        else:
            text = input("Enter the text you wish to translate: ")

            while True:
                try:
                    source_lang = input("Enter the source language (e.g., en for English): ")
                    target_lang = input("Enter the target language (e.g., es for Spanish): ")
                    translation = self.translator.translate(text, src=source_lang, dest=target_lang)
                    break  # Break out of the loop if translation is successful
                except ValueError:
                    print("Please enter valid language abbreviations. Try again.")

            self.print_visual_border()
            print(f"Original Text ({source_lang}): {text}")
            print(f"Translation ({target_lang}): {translation.text}\n")
            self.print_visual_border()

            self.update_translations_completed(self.current_user_id)

    # Method to run the application
    def run(self):
        print("Welcome to TourLingo! Please create a user before logging in if it's your first time.")

        while True:
            print("Here is the Tourlingo Menu")
            print("1. Create User")
            print("2. Log in")
            print("3. Translate text")
            print("4. User Progress")
            print("5. Exit")

            choice = input("Enter your choice (1 to 5): ")

            if choice == "1":
                username = input("Enter your username: ")
                password = input("Enter your password: ")
                self.create_user(username, password)

            elif choice == "2":
                self.login()

            elif choice == "3":
                self.translate_text()

            elif choice == "4":
                if self.current_user_id:
                    progress = self.get_user_progress(self.current_user_id)
                    self.print_visual_border()
                    print(f"Your progress: {progress} translations completed. Continue to level up your points.")
                    self.print_visual_border()
                else:
                    self.print_visual_border()
                    print("You need to log in first.")
                    self.print_visual_border()

            elif choice == "5":
                print("Thank you for using TourLingo! We are here to assist you anytime.")
                if self.db_connection.is_connected():
                    self.db_connection.close()
                break

            else:
                self.print_visual_border()
                print("Invalid choice. Please enter a number from 1 to 5.")
                self.print_visual_border()

if __name__ == "__main__":
    app = LanguageTranslatorAPP()
    app.run()
