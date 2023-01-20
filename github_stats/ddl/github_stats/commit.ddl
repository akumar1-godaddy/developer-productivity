CREATE external TABLE commit(
  repo_id int,
  repo_name string,
  github_org string,
  commit_sha string,
  message string,
  author_name string,
  author_committed_at timestamp,
  committer_name string,
  committer_committed_at timestamp,
  num_commit_parents int,
  num_file_committed int,
  commit_additions int,
  commit_deletions int,
  etl_load_utc_timestamp timestamp
)
PARTITIONED BY (
  load_date string
 )
ROW FORMAT SERDE
    'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
    STORED AS PARQUET
    LOCATION
    's3://gd-ckpetlbatch-dev-private-util/db=developer_productivity/table=commit/'
