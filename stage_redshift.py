from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from airflow.contrib.hooks.aws_hook import AwsHook
from airflow.models import Variable

class StageToRedshiftOperator(BaseOperator):
    ui_color = '#358140'
                                      
    @apply_defaults
    def __init__(self,
                 redshift_conn_id='',
                 aws_credentials_id='',
                 table='',
                 s3_bucket='',
                 s3_key='',
                 json_path='',
                 *args, **kwargs):
        super(StageToRedshiftOperator, self).__init__(*args, **kwargs)
        self.redshift_conn_id = redshift_conn_id
        self.aws_credentials_id = aws_credentials_id
        self.table = table
        self.s3_bucket = s3_bucket
        self.s3_key = s3_key
        self.json_path = json_path

    def execute(self, context):
        execution_date = context['execution_date']
        self.log.info(f'Staging {self.table} from S3 to Redshift')

        aws_hook = AwsHook(self.aws_credentials_id)
        credentials = aws_hook.get_credentials()

        s3_key_with_timestamp = self.s3_key.format(execution_date=execution_date.strftime('%Y-%m-%d'))

        redshift_hook = PostgresHook(postgres_conn_id=self.redshift_conn_id)
        copy_sql = f"""
            COPY {self.table}
            FROM 's3://{self.s3_bucket}/{self.s3_key}'
            -- Uncomment and modify the line below to enable templated time (iff runs within own S3)
            -- FROM 's3://{self.s3_bucket}/{s3_key_with_timestamp}'  
            ACCESS_KEY_ID '{credentials.access_key}'
            SECRET_ACCESS_KEY '{credentials.secret_key}'
            JSON '{self.json_path}'
            TIMEFORMAT 'auto'
            """

        self.log.info(f"Running COPY command: {copy_sql}")
        redshift_hook.run(copy_sql)
       