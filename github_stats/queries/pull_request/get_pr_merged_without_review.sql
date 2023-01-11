select "repo_name","is_merged",  "pull_number","title","author",  "pull_id", "state", "comments", "review_comments", "org_name"
from pull_request where is_merged=True  and "review_comments">0
