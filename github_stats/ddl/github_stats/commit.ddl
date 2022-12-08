CREATE external TABLE commit(
  repo_id integer COMMENT 'git generated unique id of a repo for an org',
  commit_hash string,
  message string ,
  author_name string COMMENT 'name of the author of the the modification',
  author_email string ,
  author_when_utc timestamp,
  committer_name string COMMENT 'name of the author who committed the modification',
  committer_email string COMMENT '',
  committer_when_utc timestamp COMMENT 'timestamp of when the commit was made',
  parents integer COMMENT 'the number of parents of the commit'
)
PARTITIONED BY (
  load_date string
 )
ROW FORMAT SERDE
  'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
STORED AS Parquet
    LOCATION
  's3://{bucket_name}/emr-metrics/db=developer_productivity_github_local/table=commit/'
-- commit history of a repo
