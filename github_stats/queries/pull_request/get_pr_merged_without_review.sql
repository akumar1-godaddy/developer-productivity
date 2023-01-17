select
    *
from
    pull_request_v2
where
        "review_comments_cnt"=0
order by
    created_at desc
