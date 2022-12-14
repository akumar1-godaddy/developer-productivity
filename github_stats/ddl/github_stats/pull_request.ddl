CREATE EXTERNAL TABLE `pull_request`(
  `org_name` string,
  `repo_id` int,
  `repo_name` string,
  `pull_id` int,
  `pull_number` int,
  `state` string,
  `title` string,
  `author` string,
  `author_id` int,
  `body` string,
  `created_at` timestamp,
  `updated_at` timestamp,
  `closed_at` timestamp,
  `merged_at` timestamp,
  `is_merged` boolean,
  `is_mergeable` boolean,
  `mergeable_state` string,
  `merged_by` string,
  `comments` int,
  `review_comments` int,
  `commits` int,
  `additions` int,
  `deletions` int,
  `changed_files` int,
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
  's3://gd-ckpetlbatch-dev-private-util/db=developer_productivity/table=pull_request'
TBLPROPERTIES (
  'transient_lastDdlTime'='1670966508')
