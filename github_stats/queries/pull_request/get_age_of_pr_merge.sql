select
	distinct a.repo_name,
			 a.pull_number,
			 a.state,
			 a.author,
			 a.merged_by,
			 a.additions,
			 a.comments,
			 a.review_comments,
			 date_diff('day',
					   b.created_at,
					   a.merged_at) as age_of_pr
from
	(select
		 "repo_name",
		 "pull_number",
		 "state",
		 "merged_at",
		 "is_merged",
		 "additions" ,
		 "merged_by",
		 "author",
		 "comments",
		 "review_comments"
	 from
		 "pull_request"
	 where
			 is_merged=True)a,
	(select
		 "repo_name",
		 "pull_number",
		 "state",
		 "merged_at",
		 "is_merged",
		 "additions" ,
		 "author",
		 "created_at"
	 from
		 "pull_request"
	 where
			 is_merged=False) b
where
		a.repo_name=b.repo_name
  and a.pull_number=b.pull_number
