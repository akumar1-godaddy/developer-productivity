CREATE external TABLE workflow_history(
  org_name string,
  repo_id int,
  repo_name string,
  workflow_id int,
  name string,
  path string,
  state string,
  created_at timestamp,
  updated_at timestamp,
  etl_load_utc_timestamp timestamp
)
PARTITIONED BY (
  load_date string
 )
ROW FORMAT SERDE
    'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
    STORED AS PARQUET
    LOCATION
    's3://gd-ckpetlbatch-dev-private-util/db=developer_productivity/table=workflow_history/'
