from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
from final_project_operators.stage_redshift import StageToRedshiftOperator
from final_project_operators.load_fact import LoadFactOperator
from final_project_operators.load_dimension import LoadDimensionOperator
from final_project_operators.data_quality import DataQualityOperator
from udacity.common.final_project_sql_statements import SqlQueries
from airflow.models import Variable


# Retrieve the values from Airflow variables
s3_bucket = Variable.get('s3_bucket')
s3_prefix = Variable.get('s3_prefix')

default_args = {
    'owner': 'udacity',
    'start_date': datetime(2023, 7, 16),  # Start at a fixed date in the past in stead of now (proper scheduling)
    'depends_on_past': False,
    'retries': 3,
    'retry_delay': timedelta(minutes=1),
    'catchup': False,
    'email_on_retry': False
}

dag = DAG(
    'final_project',
    default_args=default_args,
    description='Load and transform data in Redshift with Airflow',
    schedule_interval='@hourly' 
)

start_operator = DummyOperator(task_id='Begin_execution', dag=dag)

create_tables_task = PostgresOperator(
    task_id='Create_tables',
    dag=dag,
    postgres_conn_id='redshift',
    sql=[
        SqlQueries.staging_events_table_create,
        SqlQueries.staging_songs_table_create,
        SqlQueries.songplay_table_create,
        SqlQueries.user_table_create,
        SqlQueries.song_table_create,
        SqlQueries.artist_table_create,
        SqlQueries.time_table_create
    ]
)

stage_events_to_redshift = StageToRedshiftOperator(
    task_id='Stage_events',
    dag=dag,
    redshift_conn_id='redshift',
    aws_credentials_id='aws_credentials',
    table='staging_events',
    s3_bucket='udacity-dend',
    s3_key='log_data/',          # {{ execution_date.strftime("%Y-%m-%d") }}',  @templated time 
    json_path='s3://udacity-dend/log_json_path.json'
)

stage_songs_to_redshift = StageToRedshiftOperator(
    task_id='Stage_songs',
    dag=dag,
    redshift_conn_id='redshift',
    aws_credentials_id='aws_credentials',
    table='staging_songs',
    s3_bucket='udacity-dend',
    s3_key='song_data/A/A/A/',          # {{ execution_date.strftime("%Y-%m-%d") }}',  @templated time 
    json_path='auto'
)


load_songplays_table = LoadFactOperator(
    task_id='Load_songplays_fact_table',
    dag=dag,
    redshift_conn_id='redshift',
    table='songplays',
    select_sql=SqlQueries.songplay_table_insert
)

load_user_dimension_table = LoadDimensionOperator(
    task_id='Load_user_dim_table',
    dag=dag,
    redshift_conn_id='redshift',
    table='users',
    select_sql=SqlQueries.user_table_insert,
    append_mode=False
)

load_song_dimension_table = LoadDimensionOperator(
    task_id='Load_song_dim_table',
    dag=dag,
    redshift_conn_id='redshift',
    table='songs',
    select_sql=SqlQueries.song_table_insert,
    append_mode=False
)

load_artist_dimension_table = LoadDimensionOperator(
    task_id='Load_artist_dim_table',
    dag=dag,
    redshift_conn_id='redshift',
    table='artists',
    select_sql=SqlQueries.artist_table_insert,
    append_mode=False
)

load_time_dimension_table = LoadDimensionOperator(
    task_id='Load_time_dim_table',
    dag=dag,
    redshift_conn_id='redshift',
    table='time',
    select_sql=SqlQueries.time_table_insert,
    append_mode=False
)


run_quality_checks = DataQualityOperator(
    task_id='Run_data_quality_checks',
    dag=dag,
    redshift_conn_id='redshift',

)

tests = [
    # staging_events
    {'check_sql': 'SELECT COUNT(*) FROM staging_events WHERE event_id IS NULL', 'expected_result': 0},
    {'check_sql': 'SELECT COUNT(*) FROM staging_events WHERE page IS NULL', 'expected_result': 0},    
    # staging_songs
    {'check_sql': 'SELECT COUNT(*) FROM staging_songs WHERE song_id IS NULL', 'expected_result': 0},
    {'check_sql': 'SELECT COUNT(*) FROM staging_songs WHERE title IS NULL', 'expected_result': 0},    
    # songplays
    {'check_sql': 'SELECT COUNT(*) FROM songplays WHERE songplay_id IS NULL', 'expected_result': 0},
    {'check_sql': 'SELECT COUNT(*) FROM songplays WHERE start_time IS NULL', 'expected_result': 0},    
    # users
    {'check_sql': 'SELECT COUNT(*) FROM users WHERE user_id IS NULL', 'expected_result': 0},
    {'check_sql': 'SELECT COUNT(*) FROM users WHERE first_name IS NULL AND last_name IS NULL', 'expected_result': 0},    
    # songs
    {'check_sql': 'SELECT COUNT(*) FROM songs WHERE song_id IS NULL', 'expected_result': 0},
    {'check_sql': 'SELECT COUNT(*) FROM songs WHERE title IS NULL', 'expected_result': 0},    
    # artists
    {'check_sql': 'SELECT COUNT(*) FROM artists WHERE artist_id IS NULL', 'expected_result': 0},
    {'check_sql': 'SELECT COUNT(*) FROM artists WHERE name IS NULL', 'expected_result': 0},    
    # time
    {'check_sql': 'SELECT COUNT(*) FROM time WHERE start_time IS NULL', 'expected_result': 0},
    {'check_sql': 'SELECT COUNT(DISTINCT hour) FROM time', 'expected_result': 24},
    # General QC
    {'check_sql': 'SELECT COUNT(*) FROM users WHERE user_id IS NULL', 'expected_result': 0},
    {'check_sql': 'SELECT COUNT(*) FROM songs WHERE song_id IS NULL', 'expected_result': 0},
    {'check_sql': 'SELECT COUNT(*) FROM artists WHERE artist_id IS NULL', 'expected_result': 0},
    {'check_sql': 'SELECT COUNT(*) FROM time WHERE start_time IS NULL', 'expected_result': 0},
    {'check_sql': 'SELECT COUNT(*) FROM users WHERE user_id IS NULL', 'expected_result': 0},
    {'check_sql': 'SELECT COUNT(*) FROM songs WHERE duration < 0', 'expected_result': 0}   
    #other QC tests here
]


start_operator >> create_tables_task

create_tables_task >> stage_events_to_redshift
create_tables_task >> stage_songs_to_redshift

stage_events_to_redshift >> load_songplays_table
stage_songs_to_redshift >> load_songplays_table

load_songplays_table >> load_user_dimension_table
load_songplays_table >> load_song_dimension_table
load_songplays_table >> load_artist_dimension_table
load_songplays_table >> load_time_dimension_table

[load_user_dimension_table, load_song_dimension_table, load_artist_dimension_table, load_time_dimension_table] >> run_quality_checks



# #================================================================
# # tested the Dim subDAG

# from airflow.operators.subdag_operator import SubDagOperator
# # ...

# def create_dimension_subdag(parent_dag_name, child_dag_name, args):
#     subdag = DAG(
#         dag_id=f'{parent_dag_name}.{child_dag_name}',
#         default_args=args,
#         schedule_interval='@hourly',
#     )

#     load_user_dimension_table = LoadDimensionOperator(
#         task_id='Load_user_dim_table',
#         dag=subdag,
#         redshift_conn_id='redshift',
#         table='users',
#         select_sql=SqlQueries.user_table_insert,
#         append_mode=False
#     )

#     load_song_dimension_table = LoadDimensionOperator(
#         task_id='Load_song_dim_table',
#         dag=subdag,
#         redshift_conn_id='redshift',
#         table='songs',
#         select_sql=SqlQueries.song_table_insert,
#         append_mode=False
#     )

#     load_artist_dimension_table = LoadDimensionOperator(
#         task_id='Load_artist_dim_table',
#         dag=subdag,
#         redshift_conn_id='redshift',
#         table='artists',
#         select_sql=SqlQueries.artist_table_insert,
#         append_mode=False
#     )

#     load_time_dimension_table = LoadDimensionOperator(
#         task_id='Load_time_dim_table',
#         dag=subdag,
#         redshift_conn_id='redshift',
#         table='time',
#         select_sql=SqlQueries.time_table_insert,
#         append_mode=False
#     )

   
