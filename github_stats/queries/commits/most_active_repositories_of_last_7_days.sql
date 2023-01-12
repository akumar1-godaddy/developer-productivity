select
    count(*) total_commits,
    repo_name
from
    commit
where
        date("committer_committed_at" )> current_date - interval '7' day
group by
    repo_name
order by
    1 desc
