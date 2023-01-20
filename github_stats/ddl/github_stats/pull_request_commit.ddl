CREATE external TABLE pull_request_commit(
  repo_id integer COMMENT 'git generated unique id of a repo for an org',
  pr_number integer,
  commit_hash string COMMENT '',
  message string COMMENT '',
  author_name string ,
  created_at timestamp COMMENT '',
  committer_name string COMMENT '',
  committed_at timestamp,
  additions integer,
  deletions integer,
  changed_files integer,
  etl_build_utc_ts timestamp
)
PARTITIONED BY (
  load_date string
 )
ROW FORMAT SERDE
  'org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe'
STORED AS Parquet
    LOCATION
  's3://{bucket_name}/emr-metrics/db=developer_productivity_github_local/table=pull_request_commit/'

-- --
-- COMMENT ON TABLE github_pull_request_commits IS 'commits for all pull requests of a GitHub repo';
-- COMMENT ON COLUMN github_pull_request_commits.repo_id IS 'foreign key for public.repos.id';
-- COMMENT ON COLUMN github_pull_request_commits.pr_number IS 'GitHub pull request number of the commit';
-- COMMENT ON COLUMN github_pull_request_commits.hash IS 'hash of the commit';
-- COMMENT ON COLUMN github_pull_request_commits.message IS 'message of the commit';
-- COMMENT ON COLUMN github_pull_request_commits.author_name IS 'name of the author of the the modification';
-- COMMENT ON COLUMN github_pull_request_commits.author_when IS 'timestamp of when the modifcation was authored';
-- COMMENT ON COLUMN github_pull_request_commits.committer_name IS 'name of the author who committed the modification';
-- COMMENT ON COLUMN github_pull_request_commits.committer_when IS 'timestamp of when the commit was made';
-- COMMENT ON COLUMN github_pull_request_commits.additions IS 'the number of additions in the commit';
-- COMMENT ON COLUMN github_pull_request_commits.deletions IS 'the number of deletions in the commit';
-- COMMENT ON COLUMN github_pull_request_commits.changed_files IS 'the number of files changed/modified in the commit';
-- COMMENT ON COLUMN github_pull_request_commits.url IS 'GitHub URL of the commit';
-- COMMENT ON COLUMN github_pull_request_commits._mergestat_synced_at IS 'timestamp when record was synced into the MergeStat database';
