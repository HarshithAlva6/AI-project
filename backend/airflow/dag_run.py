from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime, timedelta
from dag.etl import run_etl
from dag.predict import run_predict

# Define the DAG
with DAG(
    dag_id='etl_to_predict_dag',
    start_date=datetime(2024, 1, 1),  
    schedule_interval=None,           
    catchup=False                  
) as dag:

    # Task 1: Run ETL
    etl_task = PythonOperator(
        task_id='run_etl',           
        python_callable=run_etl,     
    )

    # Task 2: Run Prediction
    predict_task = PythonOperator(
        task_id='run_predict',      
        python_callable=run_predict, 
        execution_timeout=timedelta(minutes=300),
    )

    # Define task order
    etl_task >> predict_task 
