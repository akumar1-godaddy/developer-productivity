select
    wr."repo_name",
    "name",
    "run_duration_ms"/60000 as run_time_mins,
    "event",
    "conclusion",
    wr."run_started_at_utc_ts",
    wr."created_at_utc_ts"
FROM
    workflow_run wr,
    workflow_history wh
where
    wr."workflow_id" = wh."workflow_id"
  and conclusion='failure'
order by
    3 desc
