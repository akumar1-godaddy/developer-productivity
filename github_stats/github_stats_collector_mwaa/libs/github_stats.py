import awswrangler as wr
import pandas as pd
from github import Github, Organization, Repository, GithubException
import boto3
from dataclasses import asdict
from datetime import datetime, timedelta
from urllib.parse import urlparse

from libs.utils import get_workflow_runs
from libs.records import CreateRepositoryRecord, CreateCommitRecord, CreateMemberRecord, CreatePullRecord, \
    CreatePullReviewRecord, CreateWorkflowRecord, CreateWorkflowRunRecord


def get_secret(secret_id):
    import json
    from botocore.exceptions import ClientError
    secrets_manager_client = boto3.client('secretsmanager')
    try:
        response = secrets_manager_client.get_secret_value(
            SecretId=secret_id
        )
        secret_value = response['SecretString']
        secret_dict = json.loads(secret_value)
        return secret_dict["github_pat"]
    except ClientError as e:
        print(f"Error retrieving secret: {e}")


target_s3_bucket = ''
db_name = 'developer_productivity'
secret =get_secret('github_auth_token')
github = Github(secret)
s3 = boto3.resource("s3")
_repo_commits_df = []
_repo_pulls_df = []
_repo_pulls_review_df = []
_repo_workflows_df = []
_repo_workflow_runs_df = []


def _get_orgs() -> Organization:
    """
    :rtype: :class:`github.PullRequestComment.PullRequestComment`
    """
    org = [org for org in github.get_user().get_orgs() if org.login == 'gdcorp-dna']
    return org[0]  # only returning org dna for now


def _get_org_members(org: Organization, since: datetime):
    print(f"""Get all members for the org organizations""")
    org_name = org.login
    print(f"getting members for org  {org_name}")
    members = []
    for member in org.get_members():
        member_record = CreateMemberRecord(org_name=org_name, member_id=member.id,
                                           name=member.login, role=member.type,
                                           is_site_admin=member.site_admin, created_at=member.created_at,
                                           updated_at=member.updated_at, etl_load_utc_timestamp=datetime.utcnow())

        members.append(asdict(member_record))
    df = pd.DataFrame.from_records(members)
    print(f"writing data for member")
    _write_to_s3(df, 'member_history', since)
    print(f"data load complete for member")


def _get_repos(org: Organization, since: datetime, until: datetime):
    total_repos = org.get_repos(type='internal').totalCount
    org_name = org.login
    print(f"total repository count in {org_name} is {total_repos}")
    repos = []
    for repo in org.get_repos(type='internal'):
        repository_record = CreateRepositoryRecord(repo_id=repo.id, org_name=org_name, repo_name=repo.name,
                                                   description=repo.description, size=repo.size,
                                                   default_branch=repo.default_branch, owner_name=repo.owner.name,
                                                   primary_language=repo.language, created_at=repo.created_at,
                                                   pushed_at=repo.pushed_at, updated_at=repo.updated_at,
                                                   etl_load_utc_timestamp=datetime.utcnow())
        repos.append(asdict(repository_record))
        # TODO check if get repos where updated_at condition needed
        _get_repo_commits(org_name, repo, since, until)
        _get_repo_pulls(org_name, repo, since, until)
        _get_repo_pulls_review(org_name, repo, since, until)
        # _get_repo_workflow_runs(org_name, repo, since, until)
        _get_repo_workflows(org_name=org_name, repo=repo)
    df = pd.DataFrame.from_records(repos)
    print(f"writing data for repository")
    _write_to_s3(df, 'repository_history', since)
    print(f"data load complete for repository")


def _get_repo_commits(org_name: str, repo: Repository, since: datetime, until: datetime):
    repo_id = repo.id
    # print(f"getting commits for repo {repo.name}")
    commits = []
    try:
        for commit in repo.get_commits(since=since, until=until):
            commit_obj = commit.commit
            num_commit_parents = len(commit.parents)
            num_file_committed = len(commit.files)

            commit_record = CreateCommitRecord(repo_id=repo_id, repo_name=repo.name, github_org=org_name,
                                               commit_sha=commit.sha,
                                               message=commit_obj.message, author_name=commit_obj.author.name,
                                               author_committed_at=commit_obj.author.date,
                                               committer_name=commit_obj.committer.name,
                                               committer_committed_at=commit_obj.committer.date,
                                               num_commit_parents=num_commit_parents,
                                               num_file_committed=num_file_committed,
                                               commit_additions=commit.stats.additions,
                                               commit_deletions=commit.stats.deletions,
                                               etl_load_utc_timestamp=datetime.utcnow()
                                               )
            commits.append(asdict(commit_record))
    except GithubException as ge:
        print(f'error getting the commits for repo id {repo_id} {ge}')

    if len(commits) > 0:
        df = pd.DataFrame.from_records(commits)
        _repo_commits_df.append(df)


def _get_repo_pulls(org_name: str, repo: Repository, since: datetime, until: datetime):
    # print(f"getting pulls for repo {repo.name}")
    pulls = []
    """when a PR is merged its property updated_at is updated  """
    for pull in repo.get_pulls(state='all'):
        if since <= pull.updated_at < until:
            if pull.merged_by is not None:
                merged_by = pull.merged_by.login
            else:
                merged_by = None
            pull_record = CreatePullRecord(org_name=org_name, repo_id=repo.id, repo_name=repo.name, pull_id=pull.id,
                                           pull_number=pull.number, state=pull.state, title=pull.title,
                                           author=pull.user.login, author_id=pull.user.id, body=pull.body,
                                           created_at=pull.created_at, updated_at=pull.updated_at,
                                           closed_at=pull.closed_at, merged_at=pull.merged_at,
                                           is_merged=pull.is_merged(), is_mergeable=pull.mergeable,
                                           mergeable_state=pull.mergeable_state, merged_by=merged_by,
                                           comments_cnt=pull.comments, review_comments_cnt=pull.review_comments,
                                           commits=pull.commits, additions=pull.additions, deletions=pull.deletions,
                                           changed_files=pull.changed_files, etl_load_utc_timestamp=datetime.utcnow()
                                           )
            pulls.append(asdict(pull_record))

    df = pd.DataFrame.from_records(pulls)
    _repo_pulls_df.append(df)


def _get_repo_pulls_review(org_name: str, repo: Repository, since: datetime, until: datetime):
    # print(f"getting reviews for repo {repo.name}")
    pull_reviews = []

    for review in repo.get_pulls_review_comments(since=since):
        if review.updated_at < until:
            extract_pull_number = urlparse(review.pull_request_url).path.rstrip('/').split('/')[-1]
            pull_number = int(extract_pull_number)

            review_record = CreatePullReviewRecord(org_name=org_name, repo_id=repo.id, repo_name=repo.name,
                                                   pull_request_review_id=review.id,
                                                   pull_request_url=review.pull_request_url, pull_number=pull_number,
                                                   file_path=review.path, original_commit_id=review.original_commit_id,
                                                   review_author=review.user.login, body=review.body,
                                                   created_at=review.created_at, updated_at=review.updated_at,
                                                   etl_load_utc_timestamp=datetime.utcnow()
                                                   )
            pull_reviews.append(asdict(review_record))
    df = pd.DataFrame.from_records(pull_reviews)
    _repo_pulls_review_df.append(df)


def _get_repo_workflows(org_name: str, repo: Repository):
    # print(f"getting workflows for repo {repo.name}")
    workflows = []

    for workflow in repo.get_workflows():
        workflow_record = CreateWorkflowRecord(org_name=org_name, repo_id=repo.id, repo_name=repo.name,
                                               workflow_id=workflow.id, name=workflow.name, path=workflow.path,
                                               state=workflow.state, created_at=workflow.created_at,
                                               updated_at=workflow.updated_at, etl_load_utc_timestamp=datetime.utcnow()
                                               )

        workflows.append(asdict(workflow_record))
    df = pd.DataFrame.from_records(workflows)
    _repo_workflows_df.append(df)


def _get_repo_workflow_runs(org_name: str, repo: Repository, since: datetime, until: datetime):
    print(f"getting workflow runs for repo {repo.name}")
    workflow_runs = []
    until_for_search = until - timedelta(days=1)
    search_filter = f'{since.strftime("%Y-%m-%d")}..{until_for_search.strftime("%Y-%m-%d")}'

    for workflow_run in get_workflow_runs(org_name=org_name, repo=repo.name, requester=repo._requester,
                                          created=search_filter):
        run_duration_ms = getattr(workflow_run.timing(), 'run_duration_ms', -1)
        workflow_run_record = CreateWorkflowRunRecord(org_name=org_name, repo_id=repo.id, repo_name=repo.name,
                                                      workflow_run_id=workflow_run.id,
                                                      run_number=workflow_run.run_number,
                                                      head_sha=workflow_run.head_sha,
                                                      head_branch=workflow_run.head_branch,
                                                      event=workflow_run.event, run_attempt=workflow_run.run_attempt,
                                                      status=workflow_run.status, conclusion=workflow_run.conclusion,
                                                      workflow_id=workflow_run.workflow_id,
                                                      workflow_run_url=workflow_run.url,
                                                      run_started_at_utc_ts=workflow_run.run_started_at,
                                                      created_at_utc_ts=workflow_run.created_at,
                                                      updated_at_utc_ts=workflow_run.updated_at,
                                                      run_duration_ms=run_duration_ms,
                                                      etl_load_utc_ts=datetime.utcnow()
                                                      )

        workflow_runs.append(asdict(workflow_run_record))
    df = pd.DataFrame.from_records(workflow_runs)
    _repo_workflow_runs_df.append(df)


def _write_to_s3(df: pd.DataFrame, table_name: str, since: datetime):
    if not df.empty:
        print(f"writing data for {table_name}")
        table_load_date = since.strftime("%Y-%m-%d")
        path: str = f's3://gd-ckpetlbatch-prod-developer-analytics/db={db_name}/table={table_name}/load_date={table_load_date}/data.parquet'
        wr.s3.to_parquet(
            df=df,
            path=path
            # mode='overwrite'
        )
        print(f"data load complete for {table_name}")
    else:
        print(f"data frame is empty for {table_name}")


def main(since, until):
    print(f"starting GitHub Data Extraction")
    since = datetime.strptime(since, '%Y-%m-%d')
    until = datetime.strptime(until, '%Y-%m-%d')
    print(f"value of date parameters are since:{since} .. until:{until} ")
    org = _get_orgs()
    # 1. get all the members of the org
    _get_org_members(org, since)
    # 2. get all the repos of the org
    _get_repos(org, since, until)
    # 3. get all the repo commits for the org
    final_commits_df = pd.concat(_repo_commits_df)
    _write_to_s3(final_commits_df, 'commit', since)
    # 4. get all the open pull requests for the org
    final_pulls_df = pd.concat(_repo_pulls_df)
    _write_to_s3(final_pulls_df, 'pull_request', since)
    # 5. get all the pull request review comments_cnt for all repos of the org
    final_pulls_review_comments_df = pd.concat(_repo_pulls_review_df)
    _write_to_s3(final_pulls_review_comments_df, 'pull_request_review_comment', since)
    # 6. get all the workflows for all repos of the org
    final_workflows_df = pd.concat(_repo_workflows_df)  # 6
    _write_to_s3(final_workflows_df, 'workflow_history', since)
    # final_workflow_runs_df = pd.concat(_repo_workflow_runs_df)  # 6
    # _write_to_s3(final_workflow_runs_df, 'workflow_run', since)
    return "Productivity Data Downloaded!"
