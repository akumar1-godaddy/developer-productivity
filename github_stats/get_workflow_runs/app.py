import json
import os

import awswrangler as wr
import pandas as pd
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools import Logger
from github import Github, Organization, Repository, GithubException
import boto3
from dataclasses import asdict
from datetime import datetime, timedelta
from urllib.parse import urlparse

from utils import get_workflow_runs
from records import CreateRepositoryRecord, CreateCommitRecord, CreateMemberRecord, CreatePullRecord, \
    CreatePullReviewRecord, CreateWorkflowRecord, CreateWorkflowRunRecord

logger = Logger(service="github_stats")
token = parameters.get_secret("github_auth_token", transform="json")
assert isinstance(token, dict)
target_s3_bucket = os.environ.get("TARGET_S3_BUCKET")
db_name = 'developer_productivity'

github = Github(token["github_pat"])
s3 = boto3.resource("s3")
_repo_commits_df = []
_repo_pulls_df = []
_repo_pulls_review_df = []
_repo_workflows_df = []
_repo_workflow_runs_df = []


def handler(event, context):
    logger.info(f"starting GitHub Data Extraction with input {event}")
    input_records = event.get('Records', None)
    since = event.get('since', None)
    until = event.get('until', None)
    if input_records is not None and (since is None or until is None):
        input_event = event['Records'][0]["body"]
        input_event_json = json.loads(input_event)
        since = input_event_json.get('since', None)
        until = input_event_json.get('until', None)

    if since is None or until is None:
        since = (datetime.utcnow() - timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        until = (datetime.utcnow()).replace(hour=0, minute=0, second=0, microsecond=0)
    else:
        since = datetime.strptime(since, '%Y-%m-%d')
        until = datetime.strptime(until, '%Y-%m-%d')

    logger.info(f"value of date parameters are since:{since} .. until:{until} ")
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
    final_workflow_runs_df = pd.concat(_repo_workflow_runs_df)  # 6
    _write_to_s3(final_workflow_runs_df, 'workflow_run', since)
    return "Productivity Data Downloaded!"


def _get_orgs() -> Organization:
    """
    :rtype: :class:`github.PullRequestComment.PullRequestComment`
    """
    org = [org for org in github.get_user().get_orgs() if org.login == 'gdcorp-dna']
    return org[0]  # only returning org dna for now


def _get_repos(org: Organization, since: datetime, until: datetime):
    total_repos = org.get_repos(type='internal').totalCount
    org_name = org.login
    logger.info(f"total repository count in {org_name} is {total_repos}")
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
        _get_repo_workflow_runs(org_name, repo, since, until)
        _get_repo_workflows(org_name=org_name, repo=repo)
    df = pd.DataFrame.from_records(repos)
    logger.info(f"writing data for repository")
    _write_to_s3(df, 'repository_history', since)
    logger.info(f"data load complete for repository")





def _get_repo_workflows(org_name: str, repo: Repository):
    # logger.info(f"getting workflows for repo {repo.name}")
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
    logger.info(f"getting workflow runs for repo {repo.name}")
    workflow_runs = []
    until_for_search = until - timedelta(days=1)
    search_filter = f'{since.strftime("%Y-%m-%d")}..{until_for_search.strftime("%Y-%m-%d")}'

    for workflow_run in get_workflow_runs(org_name=org_name, repo=repo.name, requester=repo._requester,
                                          status='success', created=search_filter):
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
        logger.info(f"writing data for {table_name}")
        table_load_date = since.strftime("%Y-%m-%d")
        path: str = f's3://{target_s3_bucket}/db={db_name}/table={table_name}/load_date={table_load_date}/data.parquet'
        wr.s3.to_parquet(
            df=df,
            path=path
            # mode='overwrite'
        )
        logger.info(f"data load complete for {table_name}")
    else:
        logger.info(f"data frame is empty for {table_name}")
