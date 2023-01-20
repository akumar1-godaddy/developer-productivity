CREATE external TABLE organization(
  id integer COMMENT 'git generated unique id of a repo for an org',
  name string,
  description string COMMENT '',
  disk_usage integer COMMENT '',
  login string COMMENT '',
  created_at timestamp COMMENT '',
)
PARTITIONED BY (
  load_date string
 )
ROW FORMAT SERDE
  'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
STORED AS Parquet
    LOCATION
  's3://{bucket_name}/emr-metrics/db=developer_productivity_github_local/table=organization/'
