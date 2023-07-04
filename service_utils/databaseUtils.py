import os
import mysql.connector
from mysql.connector import Error


# Function to establish a database connection
def get_database_connection():
    try:
        host = os.environ.get("DB_HOST")
        user = os.environ.get("DB_USER_NAME")
        password = os.environ.get("DB_PASSWORD")

        connection = mysql.connector.connect(host=host, database="prod_cv", user=user, password=password)
        return connection
    except Error as e:
        print("Error while connecting to MySQL", e)


def is_prohibited_user(first_name, last_name):
    try:
        # Create a database connection
        connection = get_database_connection()

        # Create a cursor
        cursor = connection.cursor()

        # Execute the query to check if the user is prohibited
        query = "SELECT is_restricted FROM interviewee WHERE first_name = %s and last_name = %s"
        cursor.execute(
            query,
            (
                first_name,
                last_name,
            ),
        )

        # Retrieve the result
        result = cursor.fetchone()
        cursor.close()
        connection.close()
        if result is None:
            return True
        elif result[0] == 1:
            # User is prohibited
            return True
        else:
            # User is not prohibited
            return False

    except mysql.connector.Error as error:
        print(f"Error while checking prohibited status: {error}")
        cursor.close()
        connection.close()


# Function to create a new account in the database
def create_account(user_data):
    try:
        # Connect to the database
        connection = get_database_connection()

        # Check if the user already exists
        if user_exists(connection, user_data["firstName"], user_data["lastName"]):
            print("User already exists")
            return

        # Insert the new user into the database
        insert_query = (
            "INSERT INTO interviewee (first_name, last_name, email, linkedin_profile) VALUES (%s, %s, %s, %s)"
        )
        user_values = (user_data["firstName"], user_data["lastName"], user_data["email"], user_data["linkedinProfile"])
        cursor = connection.cursor()
        cursor.execute(insert_query, user_values)
        connection.commit()

        # Close the database connection
        connection.close()

        print("Account created successfully")
        return True

    except Error as e:
        print("Error while connecting to MySQL", e)
        return False

    return True


def user_exists(connection, first_name, last_name):
    select_query = "SELECT * FROM interviewee WHERE first_name = %s AND last_name = %s"
    values = (first_name, last_name)
    cursor = connection.cursor()
    cursor.execute(select_query, values)
    rows = cursor.fetchall()
    return len(rows) > 0
