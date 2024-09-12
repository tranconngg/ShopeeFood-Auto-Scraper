import pandas as pd
from sqlalchemy import create_engine
from airflow.providers.mysql.hooks.mysql import MySqlHook
import datetime

def load_data():
        # Connect to MySQL using MySqlHook
        hook = MySqlHook(mysql_conn_id='my_mysql_conn')
        connection = hook.get_connection('my_mysql_conn')
        
        # Build the connection URI
        connection_uri = f"mysql+pymysql://{connection.login}:{connection.password}@{connection.host}:{connection.port}/{connection.schema}"
        engine = create_engine(connection_uri)

        table_name = "Shopeefood_Restaurant_data"
        data_final_df = pd.read_csv(r"/opt/airflow/dags/data/clean_data_restaurant.csv")
        current_date = datetime.datetime.now().strftime("%d-%m-%Y")
        data_final_df['crawled_date'] = current_date
        try:
            data_final_df.to_sql(name=table_name, con=engine, if_exists='append', index=False)
        except:
            print("Lỗi load data")