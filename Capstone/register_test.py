import sqlite3
import hashlib

#Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

#Connect to the database
connection = sqlite3.connect("dartboard.db")
cursor = connection.cursor()

#Get user details for registration
username = input("Enter a username: ")
password = input("Enter a password: ")
email = input("Enter an email (optional): ")

#Hash the password for security
hashed_password = hash_password(password)

# Insert the user into the Players table

try:
    cursor.execute('''
    INSERT INTO Players (username, password, email)
    VALUES (?, ?, ?)
    ''', (username, hashed_password, email))
    connection.commit()
    print("Registration successful!")
except sqlite3.IntegrityError as e:
    print("Error: This username is already taken.")

#Close the connection
connection.close()