-- get all commits by day by repo to see what repo is more active on any given day

select
    count(*) total_commits,
    repo_name,
    date(committer_committed_at) commit_date
from
    commit
group by
    date(committer_committed_at),
    repo_name
order by
    3 desc, 1 desc
