# Import required libraries
import os
import psycopg2
from dotenv import load_dotenv

# Initialize environment variables
load_dotenv()

class DatabaseConnection:
    # Connect to DB
    def connect_to_database():
        return psycopg2.connect(
            # Import environment variables
            host=os.getenv('host'),
            user=os.getenv('user'),
            password=os.getenv('password'),
            dbname=os.getenv('db_name'),
            port=os.getenv('port')
        )

    # Creating table found_users
    def create_table_found_users(connection):
        cursor = connection.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS found_users
                        (
                        id serial PRIMARY KEY,
                        vk_id varchar(20) UNIQUE
                        );'''
                       )
        connection.commit()
        cursor.close()
        print("(SQL) Таблица found_users = ok")

    # Checking if a user exists in the found_users table
    def check_found_users(connection, vk_id):
        cursor = connection.cursor()
        cursor.execute('SELECT vk_id FROM found_users WHERE vk_id=%s;', (vk_id,))
        result = cursor.fetchone()
        cursor.close()
        return result

    # Adding data to the found_users table
    def insert_data_found_users(connection, vk_id, offset):
        cursor = connection.cursor()
        cursor.execute('INSERT INTO found_users (vk_id) VALUES (%s);', (vk_id,))
        connection.commit()
        cursor.close()
        print(f"(SQL) Запись seen user: {vk_id}")

    # Drop table found_users
    def remove_table_found_users(connection):
        cursor = connection.cursor()
        cursor.execute('DROP TABLE IF EXISTS found_users;')
        connection.commit()
        cursor.close()
        print("(SQL) Таблица found_users удалена")

    # Disconnecting from the DB
    def disconnect_from_database(connection):
        connection.close()


    if __name__ == "__main__":
        connection = connect_to_database()
        create_table_found_users(connection)

        vk_id = "test"
        offset = 0
        insert_data_found_users(connection, vk_id, offset)
        print(check_found_users(connection, vk_id))
        disconnect_from_database(connection)