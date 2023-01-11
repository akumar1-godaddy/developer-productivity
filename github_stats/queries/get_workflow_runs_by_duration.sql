select
	distinct tb.*
from
	(SELECT
		 "name",
		 date(wr."run_started_at_utc_ts") run_date,
	wr."run_duration_ms" / 60000 as workflow_run_mins,
        wr."run_started_at_utc_ts",
        wr."repo_name",
        wr."workflow_run_id",
        wr."run_attempt",
        wr."event",
        wr."status",
        wr."conclusion",
        wr."workflow_id",
        rank() OVER (PARTITION
    BY
        date(wr."run_started_at_utc_ts")
    ORDER BY
        run_duration_ms DESC) AS rnk
FROM
	workflow_run wr,
	workflow_history wh
where
	wr."workflow_id" = wh."workflow_id" ) tb
where
	rnk<=10
