SELECT
    count(*),
    "review_author"
FROM
    "developer_productivity"."pull_request_review_comment"
group by
    "review_author"
order by
    1 desc
