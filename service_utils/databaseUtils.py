import datetime
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

def update_session_end_time(session_id):
    try:
        # Connect to the database
        connection = get_database_connection()

        # Create a cursor
        cursor = connection.cursor()

        # Execute the query to update the session end time
        query = "UPDATE session SET sessionEndTime = %s WHERE sessionID = %s"
        current_time = datetime.datetime.now()
        cursor.execute(query, (current_time, session_id))

        # Commit the transaction
        connection.commit()

        # Close the cursor and the connection
        cursor.close()
        connection.close()

        return True  # Return True to indicate successful update

    except mysql.connector.Error as error:
        print(f"Error while updating session end time: {error}")
        return False
def create_review(session_id, review):
    try:
        # Connect to the database
        connection = get_database_connection()

        # Create a cursor
        cursor = connection.cursor()

        # Execute the query to insert a new review entry
        query = "INSERT INTO reviews (sessionID, review) VALUES (%s, %s)"
        cursor.execute(query, (session_id, review))

        # Commit the transaction
        connection.commit()

        # Get the ID of the newly created review entry
        review_id = cursor.lastrowid

        # Close the cursor and the connection
        cursor.close()
        connection.close()

        return review_id  # Return the review ID

    except mysql.connector.Error as error:
        print(f"Error while inserting review: {error}")
        return None


def create_account(user_data):
    try:
        # Connect to the database
        connection = get_database_connection()
        
        # Check if the user already exists
        if user_exists(connection, user_data["firstName"], user_data["lastName"]):
            print("User already exists")
            account_id = get_account_id(connection, user_data["firstName"], user_data["lastName"])
            return account_id

        # Insert the new user into the database
        insert_query = (
            "INSERT INTO interviewee (first_name, last_name, email, linkedin_profile) VALUES (%s, %s, %s, %s)"
        )
        user_values = (user_data["firstName"], user_data["lastName"], user_data["email"], user_data["linkedinProfile"])
        cursor = connection.cursor()
        cursor.execute(insert_query, user_values)
        connection.commit()

        account_id = cursor.lastrowid

        # Close the database connection
        connection.close()

        print("Account created successfully")
        return account_id

    except Error as e:
        print("Error while connecting to MySQL", e)
        return None
    
def create_recording_entries(recording_info_list):
    try:
        # Connect to the database
        connection = get_database_connection()

        # Create a cursor
        cursor = connection.cursor()

        # Prepare the query to insert a new recording entry
        query = "INSERT INTO recording (accountID, sessionID, recordingURL, sequence) VALUES (%s, %s, %s, %s)"

        recording_ids = []
        for info in recording_info_list:
            # Execute the query for each recording
            cursor.execute(query, (info['accountID'], info['sessionID'], info['link'], info['sequence']))

            # Get the ID of the newly created recording entry and add it to the list
            recording_ids.append(cursor.lastrowid)

        # Commit the transaction
        connection.commit()

        # Close the cursor and the connection
        cursor.close()
        connection.close()

        return recording_ids  # Return the list of recording IDs

    except mysql.connector.Error as error:
        print(f"Error while creating recording entries: {error}")
        return None
    
def create_transcription_entry(account_id, session_id, sequence, text):
    try:
        # Connect to the database
        connection = get_database_connection()

        # Create a cursor
        cursor = connection.cursor()

        # Execute the query to insert a new transcription entry
        query = "INSERT INTO transcription (accountID, sessionID, sequence, text) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (account_id, session_id, sequence, text))

        # Commit the transaction
        connection.commit()

        # Get the ID of the newly created transcription entry
        transcription_id = cursor.lastrowid

        # Close the cursor and the connection
        cursor.close()
        connection.close()

        return transcription_id  # Return the transcription ID

    except mysql.connector.Error as error:
        print(f"Error while creating transcription entry: {error}")
        return None

def create_gptresponse_entry(account_id, session_id, sequence, text):
    try:
        # Connect to the database
        connection = get_database_connection()

        # Create a cursor
        cursor = connection.cursor()

        # Execute the query to insert a new gptResponse entry
        query = "INSERT INTO gptResponse (accountID, sessionID, sequence, text) VALUES (%s, %s, %s, %s)"
        cursor.execute(query, (account_id, session_id, sequence, text))

        # Commit the transaction
        connection.commit()

        # Get the ID of the newly created gptResponse entry
        gptresponse_id = cursor.lastrowid

        # Close the cursor and the connection
        cursor.close()
        connection.close()

        return gptresponse_id  # Return the gptResponse ID

    except mysql.connector.Error as error:
        print(f"Error while creating gptResponse entry: {error}")
        return None
   
def create_ttsrecording_entries(recording_info_list):
    try:
        # Connect to the database
        connection = get_database_connection()

        # Create a cursor
        cursor = connection.cursor()

        # Prepare the query to insert a new recording entry
        query = "INSERT INTO ttsrecording (accountID, sessionID, recordingURL, sequence) VALUES (%s, %s, %s, %s)"

        recording_ids = []
        for info in recording_info_list:
            # Execute the query for each recording
            cursor.execute(query, (info['accountID'], info['sessionID'], info['link'], info['sequence']))

            # Get the ID of the newly created recording entry and add it to the list
            recording_ids.append(cursor.lastrowid)

        # Commit the transaction
        connection.commit()

        # Close the cursor and the connection
        cursor.close()
        connection.close()

        return recording_ids  # Return the list of recording IDs

    except mysql.connector.Error as error:
        print(f"Error while creating ttsrecording entries: {error}")
        return None

    
def create_session(account_id):
    try:
        # Connect to the database
        connection = get_database_connection()

        # Create a cursor
        cursor = connection.cursor()

        # Execute the query to insert a new session
        query = "INSERT INTO session (accountID) VALUES (%s)"
        cursor.execute(query, (account_id,))

        # Commit the transaction
        connection.commit()

        # Get the ID of the newly created session
        session_id = cursor.lastrowid


        # Close the cursor and the connection
        cursor.close()
        connection.close()

        return session_id  # Return the session ID

    except mysql.connector.Error as error:
        print(f"Error while creating session: {error}")
        return None
    
def get_session_info(session_id):
    try:
        # Connect to the database
        connection = get_database_connection()

        # Create a cursor
        cursor = connection.cursor()

        # Execute the query to get the session information
        query = "SELECT * FROM session WHERE sessionID = %s"
        cursor.execute(query, (session_id,))

        # Fetch the result
        result = cursor.fetchone()

        # Fetch column names from cursor.description
        column_names = [column[0] for column in cursor.description]

        # Close the cursor and the connection
        cursor.close()
        connection.close()

        # Return the session information as a dictionary
        return dict(zip(column_names, result))

    except mysql.connector.Error as error:
        print(f"Error while getting session info: {error}")
        return None


def get_account_id(connection, first_name, last_name):
    try:
        # Create a cursor
        cursor = connection.cursor()

        # Execute the query to get the account ID
        query = "SELECT accountID FROM interviewee WHERE first_name = %s AND last_name = %s"
        cursor.execute(query, (first_name, last_name))

        # Fetch the result
        result = cursor.fetchone()

        # Close the cursor
        cursor.close()

        if result is not None:
            return result[0]  # Return the account ID
        else:
            return None
    except Error as e:
        print("Error while fetching account ID", e)
        return None



def user_exists(connection, first_name, last_name):
    select_query = "SELECT * FROM interviewee WHERE first_name = %s AND last_name = %s"
    values = (first_name, last_name)
    cursor = connection.cursor()
    cursor.execute(select_query, values)
    rows = cursor.fetchall()
    return len(rows) > 0
