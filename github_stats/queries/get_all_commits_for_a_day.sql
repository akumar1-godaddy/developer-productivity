select "repo_name", "commit_sha", "author_name", "committer_name", "num_file_committed", "commit_additions",
       "commit_deletions" from commit where "load_date"= '2022-12-14' order by "commit_additions" desc
