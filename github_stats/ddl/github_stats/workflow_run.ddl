CREATE external TABLE workflow_run(
  org_name string,
  repo_id int,
  repo_name string,
  workflow_run_id int,
  head_branch string,
  head_sha string,
  run_number int,
  run_attempt int,
  event string,
  status string,
  conclusion string,
  workflow_id int,
  workflow_run_url string,
  run_started_at_utc_ts timestamp,
  created_at_utc_ts timestamp,
  updated_at_utc_ts timestamp,
  etl_load_utc_ts timestamp
)
PARTITIONED BY (
  load_date string
 )
ROW FORMAT SERDE
    'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
    STORED AS PARQUET
    LOCATION
    's3://gd-ckpetlbatch-dev-private-util/db=developer_productivity/table=workflow_run/'
