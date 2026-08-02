from datetime import datetime, timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator, ShortCircuitOperator

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime(2026, 8, 1),
    'email_on_failure': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=10),
}

def train_collaborative_task():
    from ml.train_collaborative import train_als_model
    train_als_model()

def train_content_task():
    from ml.train_content import train_content_model
    train_content_model()

def evaluation_gate_task() -> bool:
    from ml.evaluate import evaluate_recommender
    metrics = evaluate_recommender(k=10)
    beats_baseline = metrics.get("beats_baseline", False)
    print(f"Evaluation Gate result: beats_baseline={beats_baseline}")
    return beats_baseline

def write_similarity_table_task():
    from ml.export_similarity import export_precomputed_similarity
    export_precomputed_similarity()

with DAG(
    'anime_train_recommender_dag',
    default_args=default_args,
    description='Weekly ML training and precomputed similarity matrix update pipeline',
    schedule_interval='@weekly',
    catchup=False,
) as dag:

    t_train_collab = PythonOperator(
        task_id='train_collaborative',
        python_callable=train_collaborative_task,
    )

    t_train_content = PythonOperator(
        task_id='train_content',
        python_callable=train_content_task,
    )

    t_gate = ShortCircuitOperator(
        task_id='evaluation_gate',
        python_callable=evaluation_gate_task,
    )

    t_export = PythonOperator(
        task_id='write_similarity_table',
        python_callable=write_similarity_table_task,
    )

    [t_train_collab, t_train_content] >> t_gate >> t_export
