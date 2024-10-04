import pandas as pd
import logging
from utils.postgres_connecter.db_connection import connect_to_postgres
from configs.config_system import SYSTEM_CONFIG

class PostgresHandler:
    def __init__(self):
        self.host = SYSTEM_CONFIG.POSTGRES_HOST
        self.database_name = SYSTEM_CONFIG.POSTGRES_DB_NAME
        self.password = SYSTEM_CONFIG.POSTGRES_PASSWORD
        self.user = SYSTEM_CONFIG.POSTGRES_USER
        self.port = SYSTEM_CONFIG.POSTGRES_PORT
        self.TIMEOUT = SYSTEM_CONFIG.CONNECTION_TIMEOUT
        self.connection, error = connect_to_postgres(
            host=self.host,
            database_name=self.database_name,
            user=self.user,
            password=self.password,
            port=self.port,
            max_timeout=self.TIMEOUT
        )
        self.create_table()
        if self.connection is None:
            logging.error(f"Error: {error.upper()}")

    def create_table(self):
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS sales_force.log_chat_sales_force(
            id SERIAL PRIMARY KEY,
            user_name VARCHAR(255) NOT NULL,
            session_id VARCHAR(255) NOT NULL,
            total_token INT,
            total_cost FLOAT,
            time_request VARCHAR(255),
            status VARCHAR(255),
            error_message TEXT,
            human_chat TEXT,
            bot_chat TEXT
        )
        '''
        try:    
            with self.connection.cursor() as cusor:
                cusor.execute(create_table_query)
                self.connection.commit()
                logging.info("Table created successfully in PostgreSQL")
        except Exception as e:
            logging.error(f"Error create table : {e}")
            self.connection.rollback()

    def insert_data(self, user_name: str, session_id: str, total_token: int, toal_cost: float,
                    time_request: str, status: str, error_message: str, human_chat: str, bot_chat: str):
        
        insert_query = '''
        INSERT INTO sales_force.log_chat_sales_force(user_name, session_id, total_token, total_cost, time_request, status, error_message, human_chat, bot_chat)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insert_query, (user_name, session_id, total_token, toal_cost, time_request, status, error_message, human_chat, bot_chat))
                self.connection.commit()
                logging.info("Data inserted successfully in PostgreSQL")
        except Exception as e:
            logging.error(f"Error insert data: {e}")
            self.connection.rollback()
    
    def get_logging(self):
        select_query = '''
        SELECT * FROM sales_forces.log_chat_sales_force
        '''
        df = pd.read_sql_query(select_query, self.connection)
        self.connection.commit()
        return df
        
    
if __name__ == "__main__":
    postgres_handle = PostgresHandler()
    postgres_handle.create_table()
    postgres_handle.connection.close()