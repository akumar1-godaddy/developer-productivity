CREATE external TABLE repository(
  id integer COMMENT 'git generated unique id of a repo for an org',
  organization_name string,
  name string COMMENT '',
  description string COMMENT '',
  size integer COMMENT 'KBs',
  default_branch string COMMENT '',
  owner_name string COMMENT '',
  last_modified timestamp COMMENT '',
  primary_language string,
  pushed_at timestamp,
  updated_at timestamp
)
PARTITIONED BY (
  load_date string
 )
ROW FORMAT SERDE
  'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
STORED AS Parquet
    LOCATION
  's3://{bucket_name}/emr-metrics/db=developer_productivity_github_local/table=organization/'

-- snap everything pulled every day.
--
-- metadata snap pulled every day
--
