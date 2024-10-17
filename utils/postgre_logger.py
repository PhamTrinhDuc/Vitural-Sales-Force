import pandas as pd
import logging
import psycopg2
from configs.config_system import SYSTEM_CONFIG

class PostgreHandler:
    def __init__(self):
        self.host = SYSTEM_CONFIG.POSTGRES_HOST
        self.database_name = SYSTEM_CONFIG.POSTGRES_DB_NAME
        self.password = SYSTEM_CONFIG.POSTGRES_PASSWORD
        self.user = SYSTEM_CONFIG.POSTGRES_USER
        self.port = SYSTEM_CONFIG.POSTGRES_PORT
        self.max_timeout = SYSTEM_CONFIG.POSTGRE_TIMEOUT
        self.connection, error = self.connect_to_postgre()
        # self.create_table()

        if self.connection is None:
            logging.error(f"Error: {error.upper()}")
    
    def connect_to_postgre(self):
        try:
            conn_string = f"""host={self.host} dbname={self.database_name} 
            user={self.user} password={self.password} port={self.port} connect_timeout={self.max_timeout}"""
            conn = psycopg2.connect(conn_string)
            cursor = conn.cursor()
            cursor.execute("SELECT 1")
            result = cursor.fetchone()

            if result[0] == 1:
                message = f"Successful connection to PostgreSQL database {self.database_name} !"
            else:
                cursor.close()
                conn.close()
                message = "Connection failed: Unable to verify connection"
            return conn, message
            
        except psycopg2.errors.OperationalError as e:
            if "timeout expired" in str(e):
                return None, f"Error: Connection timeout after {self.max_timeout} seconds"
            else:
                return None, f"Connection error: {e}"
        
        except Exception as e:
            return None, f"Unknown error: {e}"
    

    def create_table(self):
        create_table_query = '''
        CREATE TABLE IF NOT EXISTS sales_force.log_chat_sales_force(
            id SERIAL PRIMARY KEY,
            user_name VARCHAR(50) NOT NULL,
            phone_number VARCHAR(20) NOT NULL,
            session_id VARCHAR(100) NOT NULL,
            object_product TEXT,
            date_request TIMESTAMP,
            total_token INT,
            total_cost FLOAT,
            time_request VARCHAR(255),
            status VARCHAR(100),
            error_message TEXT,
            name_bot TEXT,
            rewritten_human TEXT,
            human TEXT,
            ai TEXT
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

    def insert_data(self, user_name: str, phone_number: str, session_id: str, object_product: str, 
                    date_request: str, total_token: int, toal_cost: float, time_request: str, status: str, 
                    error_message: str, name_bot: str, rewritten_human: str, human: str, ai: str):
        
        insert_query = '''
        INSERT INTO sales_force.log_chat_sales_force(user_name, phone_number, session_id, object_product, 
            date_request, total_token, total_cost, time_request, status, error_message, 
            name_bot, rewritten_human, human, ai)
        VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        '''

        try:
            with self.connection.cursor() as cursor:
                cursor.execute(insert_query, (user_name, phone_number, session_id, object_product, 
                                              date_request, total_token, toal_cost, time_request, status, error_message, 
                                              name_bot, rewritten_human, human, ai))
                self.connection.commit()
                logging.info("Data inserted successfully in PostgreSQL")
        except Exception as e:
            logging.error(f"Error insert data to database: {e}")
            self.connection.rollback()
    
    def get_logging(self):
        select_query = '''
        SELECT * FROM sales_forces.log_chat_sales_force
        '''
        df = pd.read_sql_query(select_query, self.connection)
        self.connection.commit()
        return df
        
    
if __name__ == "__main__":
    postgres_handle = PostgreHandler()
    postgres_handle.create_table()
    postgres_handle.connection.close()
    