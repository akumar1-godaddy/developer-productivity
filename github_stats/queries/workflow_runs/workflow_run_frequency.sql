select
    count(*) runs_in_last_week,
    wr.repo_name
FROM
    workflow_run wr,
    workflow_history wh
where
    wr."workflow_id" = wh."workflow_id"
  and date("run_started_at_utc_ts")> current_date - interval '7' day
group by
    wr.repo_name
order by
    1 desc
