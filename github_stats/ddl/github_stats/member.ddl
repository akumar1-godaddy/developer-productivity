CREATE external TABLE member(
  id integer COMMENT 'git generated unique id of a repo for an org',
  login string,
  name string COMMENT '',
  role string COMMENT '',
  email string COMMENT '',
  is_site_admin boolean COMMENT '',
  type string COMMENT '',
  updated_at timestamp COMMENT '',
)
PARTITIONED BY (
  load_date string
 )
row format delimited
fields terminated by ','
stored as textfile
LOCATION
  's3://{bucket_name}/emr-metrics/db=emr_cluster_metrics/table=emr_cluster_audit/'
TBLPROPERTIES ("skip.header.line.count"="1");


    -- Members
