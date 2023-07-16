from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.contrib.hooks.aws_hook import AwsHook

class LoadDimensionOperator(BaseOperator):
    ui_color = '#80BD9E'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id='',
                 table='',
                 select_sql='',
                 append_mode=True,
                 *args, **kwargs):
        super(LoadDimensionOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.table = table
        self.select_sql = select_sql
        self.append_mode = append_mode

    def execute(self, context):
        self.log.info(f'Loading data into {self.table}')

        redshift_hook = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        if self.append_mode:
            insert_sql = f"""
                INSERT INTO {self.table}
                {self.select_sql}
                """
        else:
            truncate_sql = f"""
                TRUNCATE TABLE {self.table};
                """
            insert_sql = f"""
                {truncate_sql}
                {self.select_sql}
                """

        self.log.info(f"Running SQL command: {insert_sql}")
        redshift_hook.run(insert_sql)



