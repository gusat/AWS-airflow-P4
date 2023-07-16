# mig's AF ELT Data Pipeline for P4
This README provides an overview of the ELT data pipeline implemented in this final project (p4). 
It describes the main operators, their functionality, and the associated DAG calls. 

## Files
All the reference PJ files are in their default locations, also including 
/home/workspace/set_connections_and_variables.sh
/home/workspace/airflow/plugins/final_project_operators/data_quality.py
/home/workspace/airflow/plugins/final_project_operators/load_fact.py
/home/workspace/airflow/plugins/custom_operators/load_dimensions.py
/home/workspace/airflow/plugins/final_project_operators/stage_redshift.py
/home/workspace/airflow/dags/udacity/common/final_project_sql_statements.py
/home/workspace/airflow/dags/cd0031-automate-data-pipelines/project/starter/final_project.py


## Operators
### StageToRedshiftOperator
The StageToRedshiftOperator is responsible for loading JSON formatted files from Amazon S3 to Amazon Redshift. 
Core function: dynamically creates and runs a SQL COPY statement based on the provided parameters.

### LoadFactOperator
The LoadFactOperator is responsible for loading data into a fact table in Redshift. 
Core: It runs an SQL INSERT command to insert data into the specified table.

### LoadDimensionOperator
The LoadDimensionOperator is responsible for loading data into a dimension table in Redshift. 
Core: It supports both append-only and delete-load functionality, as tested.

### DataQualityOperator
The DataQualityOperator is responsible for performing the dyn. QC tests, according to the 15+ calls implemented in DAG.
Core: It must help to detect data Q issues, key/field mismatches, unwanted defaults etc.

## Custom SQL Queries
The SqlQueries class contains the SQL queries used in the data pipeline for inserting data into fact and dimension tables.
Additionally it can also CREATE the tables --once only!-- within the DAG, for testing & stand-alone functionality; 
Normally any table CREATE functions will be implemented production-level with external operators (outside the DAG).

## DAG Structure
The DAG structure is defined in the final_project Airflow DAG file.

## Additional Functionality
The data pipeline allows for additional functionality such as logging, op mode switching, data quality checks - as the 15-20 basic tests provided for the DataQuality checks.
Dim subDAG was implemented and tested early; subDAG eventually commented out to accelerate the new subsequent features' testing.

# Extra Features Guidelines
## Timed Template in Stage Operator
To enable the timed template functionality in the StageToRedshiftOperator, follow these steps:
1. In the DAG definition, set the `s3_key` parameter of the StageToRedshiftOperator to include the time template as a string. 
For example: s3_key='log_data/{{ execution_date.strftime("%Y-%m-%d") }}'
2. This will dynamically replace `{{ execution_date.strftime("%Y-%m-%d") }}` with the execution date of the DAG run in the format `YYYY-MM-DD`.
By default this is disabled when using the s3 paths (resource efficiency and $ savings).

## Switching between Append-Only and Delete-Load Dim. functionality
To switch between append-only and delete-load Dim. functionality in the DAG (calls):
1. In the DAG definition, set the `append_mode` parameter of the LoadDimensionOperator to `True` for append-only mode or `False` for delete-load mode.
2. Depending on the value of `append_mode`, the LoadDimensionOperator will perform the corresponding data loading operation.
## Switch Option in Load Dimension Operator
The LoadDimensionOperator supports both append-only and delete-load functionality. To switch between these modes, follow these steps:
1. In the DAG definition, set the `append_mode` parameter of the LoadDimensionOperator to `True` for append-only mode or `False` for delete-load mode. 
For example: append_mode=True
2. If `append_mode` is set to `True`, the operator will perform an `INSERT INTO` operation to append data to the dimension table.
3. If `append_mode` is set to `False`, the operator will first execute a `TRUNCATE TABLE` command to delete all existing data from the dimension table, followed by the `INSERT INTO` operation to load new data.
By default this is disabled when using the s3 paths (resource efficiency and $ savings).

## Hooks and Dynamic Parameters
The operators use hooks to establish a connection with Redshift and execute SQL statements. The parameters are passed dynamically to generate the SQL statements.
1. The `redshift_conn_id` parameter of the operators is set to the connection ID of the Redshift connection in Airflow.
2. The SQL statements in the operators use f-strings to dynamically inject the parameters into the SQL queries.

## DB Infrastructure: Amazon Redshift
We have implemented and tested using both the hosted (pricey $$) and the serverless (quasi-free for $300, the default here) versions of AWS  Redshift.
Classic RS: Use the provided U_IaC_v1.1.ipynb (as my bonus automation) to create / pause / restart the AWS resources and RS cluster, w/o any need for an AWS console.

## Running the Pipeline
To run the data pipeline, ensure that Apache Airflow is properly set up and configured. Import the DAG file into the Airflow environment and trigger the DAG manually or based on a schedule.
Expectation bounds: The DAG including a one-time 7x table creation runs w/ RS sv-less in ~90sec on the "A" paths (no local copies) subset below
s3_bucket='udacity-dend',
s3_key='song_data/A/'

## Conclusion
This ELT data pipeline provides a scalable and automated solution for loading data from various sources into Amazon Redshift. 
By leveraging Airflow's powerful features and custom operators, the pipeline enables efficient data processing and transformation.

If you have any questions please don't hesitate to reach out to mig@zurich.ibm.com

## Some toy analytics performed on the test data subset 

A) Baseline
SELECT COUNT(*) FROM songs; => 628
SELECT COUNT(*) FROM artists; => 611

B) What are the Top5 most played artists?
SELECT a.name AS artist_name, COUNT(*) AS play_count
FROM songplays sp
JOIN artists a ON sp.artist_id = a.artist_id
GROUP BY a.name
ORDER BY play_count DESC
LIMIT 5; =>
artist_name  play_count
Black Eyed Peas	3
The Rolling Stones	2
The Smiths	2
The Verve	2
Pearl Jam	1


C) What are the Top3 most played songs?
SELECT s.title AS song_title, a.name AS artist_name, COUNT(*) AS play_count
FROM songplays sp
JOIN songs s ON sp.song_id = s.song_id
JOIN artists a ON sp.artist_id = a.artist_id
GROUP BY s.title, a.name
ORDER BY play_count DESC
LIMIT 1; =>
song_title artist_name play_count
Let's Get It Started	        Black Eyed Peas	    3
Angie (1993 Digital Remaster)	The Rolling Stones	2
Bitter Sweet Symphony	        The Verve	        2


D) What's Sparkify's time histogram, i.e., busy_play_time?
SELECT hour, COUNT(*) AS play_count
FROM time t
JOIN songplays sp ON t.start_time = sp.start_time
GROUP BY hour
ORDER BY play_count DESC; =>
hour 	play_count
15	3
21	3
17	3


## License
This project is licensed under the MIT License.
