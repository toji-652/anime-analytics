from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 8, 1),
    'email_on_failure': False,
    'retries': 2,
    'retry_delay': timedelta(minutes=5),
}

def fetch_updated_titles_task():
    from ingestion.incremental_sync import IncrementalSync
    sync = IncrementalSync()
    sync.run_incremental_sync(max_titles=20)

with DAG(
    'anime_incremental_dag',
    default_args=default_args,
    description='Daily incremental API sync and dimensional update pipeline',
    schedule_interval='@daily',
    catchup=False,
) as dag:

    t_fetch = PythonOperator(
        task_id='fetch_updated_titles',
        python_callable=fetch_updated_titles_task,
    )

    t_spark_flatten = BashOperator(
        task_id='spark_flatten',
        bash_command='python /opt/airflow/processing/spark_jobs/flatten_metadata.py',
    )

    t_dbt_run = BashOperator(
        task_id='dbt_run_incremental',
        bash_command='cd /opt/airflow/warehouse && dbt run',
    )

    t_dbt_test = BashOperator(
        task_id='dbt_test',
        bash_command='cd /opt/airflow/warehouse && dbt test',
    )

    t_fetch >> t_spark_flatten >> t_dbt_run >> t_dbt_test
