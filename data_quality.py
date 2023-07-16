from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.contrib.hooks.aws_hook import AwsHook

class DataQualityOperator(BaseOperator):
    ui_color = '#89DA59'

    @apply_defaults
    def __init__(self,
                 redshift_conn_id='',
                 tests=None,
                 *args, **kwargs):
        super(DataQualityOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.tests = tests or []  # Ensure an empty list if tests is None

    def execute(self, context):
        self.log.info('Running data quality checks')

        redshift_hook = PostgresHook(postgres_conn_id=self.redshift_conn_id)

        for test in self.tests:
            check_sql = test['check_sql']
            expected_result = test['expected_result']

            self.log.info(f"Running SQL: {check_sql}")
            records = redshift_hook.get_records(check_sql)
            result = records[0][0]

            if result != expected_result:
                raise ValueError(f"Data quality check failed. Expected result: {expected_result}, Actual result: {result}")