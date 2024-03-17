import random
import string
import mysql.connector
import hashlib
import secrets
import json
import logging


def logging_system():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        filename="splunklogs.log"
    )


logging_system()

def load_db_config(file_path):
    with open(file_path, 'r') as file:
        return json.load(file)


def log_function_call(func):
    """Decorator to log function calls."""
    def wrapper(*args, **kwargs):
        logging.info(f"Called function: {func.__name__}")
        return func(*args, **kwargs)
    return wrapper


# File path to the json file
db_config_path = 'C:\\Users\\Juan\\OneDrive\\Desktop\\dbcredentials.json'
db_config = load_db_config(db_config_path)


def salting():
    return secrets.token_hex(16)  # 16 bytes for the salt

# Hashing functions to provide more security
def hash_password(password, salt):
    password = password.encode('utf-8')
    salt = salt.encode('utf-8')
    hashed_password = hashlib.sha256(salt + password).hexdigest()
    return hashed_password

# Creates a new account
# @log_function_call
def new_account():
    user_name = input("Enter your username: ")
    service_name = input("Enter the service name: ")
    password_length = int(input("Enter the desired password length: "))
    
    if password_length <= 0:
        print("Password length should be a positive integer.")
        return
    random_password = generate_random_password(password_length)
    print(f"Your Password is: {random_password}")
    salt = salting()
    hashed_password = hash_password(random_password, salt)
    save_password(hashed_password, user_name, service_name)
    logging.debug(f"The Account {service_name} has been created")

def Delete_Account():
    serviceToDelete = input("What service account would you like to delete?: ")
    conn = mysql.connector.connect(**db_config)
    cursor = conn.cursor()
    delete_query = "DELETE FROM passwords_info WHERE service_name = %s"
    data = (serviceToDelete,)

    cursor.execute(delete_query, data)
    conn.commit()
    print(
        f"Account '{serviceToDelete}' and associated data deleted successfully.")
    logging.debug(f"The Account {serviceToDelete} has been deleted.")


def generate_random_password(length):
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for _ in range(length))
    return password


def save_password(hashed_password, user_name, service_name):
    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        insert_query = """
        INSERT INTO passwords_info (user_name, pass_hash, service_name)
        VALUES (%s, %s, %s)
        """
        data = (user_name, hashed_password, service_name)

        cursor.execute(insert_query, data)
        conn.commit()

        print("Password has been saved to the database!")

    except mysql.connector.Error as e:
        print("Error:", e)
    

    finally:
        if 'conn' in locals() and conn.is_connected():
            cursor.close()
            conn.close()
            print("Database connection closed.")


def get_account_data():
    service_name = input("Enter the service name: ")

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
        # Execute the SQL query to retrieve username and password for the specified service_name
        query = "SELECT user_name, pass_hash FROM passwords_info WHERE service_name = %s"
        cursor.execute(query, (service_name,))

        # Fetch the result
        result = cursor.fetchone()

        if result:
            username, password = result
            print(
                f"Service: {service_name}\nUsername: {username}\nPassword: {password}")
        else:
            print(f"No data found for service: {service_name}")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        cursor.close()
        conn.close()
    logging.debug(f"The Account {service_name} has been viewed")



def update_account():
    service_name = input("Enter the service name: ")
    userName = input("Enter your username: ")
    new_password = input("Enter your new password:")

    try:
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()
     

        query = "UPDATE passwords_info SET pass_hash = %s WHERE service_name = %s AND user_name = %s"
        cursor.execute(query, (new_password, service_name, userName))
        conn.commit()

        if cursor.rowcount > 0:
            print(f"Password updated successfully for service: {service_name}")
        else:
            print(f"No data found for service: {service_name}")

    except mysql.connector.Error as err:
        print(f"Error: {err}")

    finally:
        cursor.close()
        conn.close()
    

    logging.debug(f"The Account {service_name} has been updated")



def main_menu():
    option = ""
    while True:
        print("Password Menu ---")
        print("1 - Create New Account")
        print("2 - Delete Account")
        print("3 - View an Account")
        print("4 - Update an Account")
        print("0 - Exit Program")
        option = input("Enter Menu Option: ")
        if option == "0":
            print("Goodbye")
            break

        elif option == "1":
            new_account()
        elif option == "2":
            Delete_Account()
        elif option == "3":
            get_account_data()
        elif option == '4':
            update_account()


if __name__ == "__main__":
    main_menu()
