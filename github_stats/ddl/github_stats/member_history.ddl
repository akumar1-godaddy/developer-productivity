CREATE EXTERNAL TABLE `member_history`(
  `org_name` string,
  `member_id` int,
  `name` string,
  `role` string,
  `email` string,
  `is_site_admin` boolean,
  `created_at` timestamp,
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
  's3://gd-ckpetlbatch-dev-private-util/db=developer_productivity/table=member_history'
TBLPROPERTIES (
  'transient_lastDdlTime'='1670961955')
