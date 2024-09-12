from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.utils.dates import days_ago

from crawler.crawl_list_restaurant import crawl_list_restaurant
from crawler.crawl_restaurant_details import crawl_restaurant_details_thread
from report.process_data import process_get_report
from report.send_email import send_email
from load.load_to_mysql import load_data

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 1,
}

dag = DAG(
    'shopeefood_crawl_and_report', 
    default_args=default_args,
    description='A DAG to crawl ShopeeFood data, process it, and send a report',
    schedule_interval='@daily',
    catchup=False,
)

crawl_list_task = PythonOperator(
    task_id='crawl_list_restaurant',
    python_callable=crawl_list_restaurant,
    dag=dag,
)

crawl_details_task = PythonOperator(
    task_id='crawl_restaurant_details',
    python_callable=crawl_restaurant_details_thread,
    provide_context=True,
    dag=dag,
)

process_task = PythonOperator(
    task_id='process_report',
    python_callable=process_get_report,
    dag=dag,
)

send_report_task = PythonOperator(
    task_id='send_report',
    python_callable=send_email,
    dag=dag,
)

loadDB_task = PythonOperator(
    task_id='load_db',
    python_callable=load_data,
    dag=dag,
)

crawl_list_task >> crawl_details_task >> process_task >> send_report_task >> loadDB_task
