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

-- org snap pulled every day
-- metadata snap pulled every day
--
    * Learned a lot about Godaddy Domains and Data Science Models used to Power Godaddy Domain Search,


    * Learned a lot about Godaddy Domains and Data Science Models used to Power Godaddy Domain Search, After Market Business, Domain Bidding, DNS, and Advertisement Management Technology and AdServers.
* Saved Cost for the company by getting rid expensive operations to change S3 object ownership, implemented solutions in a way which need little ops support like Great Expectations for Data Quality and are easy to use.
    * Provided in-house solution for Advertisement Data Mart, I was just given the requirement to parse logs and source the data from Logs but I went beyond that and even sourced the data from Kevel Ad Management APIs, pulling data directly into Spark and using to provide valuable data for Advertisement Management.
    * Joined Forces with DRI architect Chungwei for Media Solutions Data and Doing PRs for EMR serverless, also worked with Data Science teams to work on AWS issues.
* Regular contributor in Airflow- Guild to join forces and help engineers with issues on MWAA, general Airflow questions etc.. Patrick Dinnen
