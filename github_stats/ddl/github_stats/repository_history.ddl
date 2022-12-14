CREATE EXTERNAL TABLE `repository_history`(
  `repo_id` int,
  `github_org` string,
  `repo_name` string,
  `description` string,
  `size` int,
  `default_branch` string,
  `owner_name` string,
  `primary_language` string,
  `created_at` timestamp,
  `pushed_at` timestamp,
  `updated_at` timestamp,
  `etl_load_utc_timestamp` timestamp)
PARTITIONED BY (
  `load_date` string)
ROW FORMAT SERDE
  'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
STORED AS INPUTFORMAT
  'org.apache.hadoop.hive.ql.io.parquet.MapredParquetInputFormat'
OUTPUTFORMAT
  'org.apache.hadoop.hive.ql.io.parquet.MapredParquetOutputFormat'
LOCATION
  's3://gd-ckpetlbatch-dev-private-util/db=developer_productivity/table=repository_history'
TBLPROPERTIES (
  'transient_lastDdlTime'='1670963524')
