import sqlite3
import hashlib

# Function to hash passwords
def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

#Connect to the database
connection = sqlite3.connect("dartboard.db")
cursor = connection.cursor()

#Get login details
username = input("Enter your username: ")
password = input("Enter your password: ")

#Hash the entered password
hashed_password = hash_password(password)

#Check if the username and password match
cursor.execute('''
SELECT * FROM Players
WHERE username = ? AND password = ?
''', (username, hashed_password))
user = cursor.fetchone()

if user:
    print(f"Login successful! Welcome {username}.")
else:
    print("Invalid username or password.")

#Close the connection
connection.close()



