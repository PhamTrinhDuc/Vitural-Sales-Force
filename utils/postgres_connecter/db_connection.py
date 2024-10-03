import psycopg2
from typing import Optional
from icecream import ic


def connect_to_postgres(host: str, database_name: str, password: str, user: str,
                        port: Optional[str] = 5432, max_timeout: Optional[int] = 10):
    try:
        conn_string = f"host={host} dbname={database_name} user={user} password={password} port={port} connect_timeout={max_timeout}"
        conn = psycopg2.connect(conn_string)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()

        if result[0] == 1:
            message = f"Successful connection to PostgreSQL database {database_name} !"
        else:
            cursor.close()
            conn.close()
            message = "Connection failed: Unable to verify connection"
        return conn, message
        
    except psycopg2.errors.OperationalError as e:
        if "timeout expired" in str(e):
            return None, f"Error: Connection timeout after {max_timeout} seconds"
        else:
            return None, f"Connection error: {e}"
    
    except Exception as e:
        return None, f"Unknown error: {e}"
    
if __name__ =="__main__":
    connection, status_message = connect_to_postgres(
        host="127.0.0.1",
        database_name="chatbot",
        user="postgres",
        password='duc8504@@',
        max_timeout=6
    )
    ic(status_message.upper())