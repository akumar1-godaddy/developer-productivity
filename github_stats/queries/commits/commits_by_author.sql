select
    count(*) total_committs,
    sum("commit_additions") additions,
    "author_name",
    repo_name,
    sum("num_file_committed") files,
    sum("commit_deletions") deletions
from
    commit
group by
    repo_name,
    author_name
order by
    3
