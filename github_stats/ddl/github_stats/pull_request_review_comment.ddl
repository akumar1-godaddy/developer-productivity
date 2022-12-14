CREATE external TABLE pull_request_review_comment(
  org_name string,
  repo_id integer,
  repo_name string,
  pull_request_review_id integer,
  pull_request_url string,
  pull_number integer,
  file_path string,
  original_commit_id string,
  review_author string,
  body string,
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
    's3://gd-ckpetlbatch-dev-private-util/db=developer_productivity/table=pull_request_review_comment/'
