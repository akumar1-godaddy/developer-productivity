import awswrangler as wr
import pandas as pd
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools import Logger
from github import Github
from github import Organization, Repository, GithubException
import boto3
from dataclasses import asdict
from datetime import datetime, timedelta
from urllib.parse import urlparse

from records import CreateRepositoryRecord, CreateCommitRecord, CreateMemberRecord, CreatePullRecord, \
    CreatePullReviewRecord, CreateWorkflowRecord, CreateWorkflowRunRecord

logger = Logger(service="github_stats")
token = parameters.get_secret("github_auth_token", transform="json")
assert isinstance(token, dict)

github = Github(token["github_pat"])
s3 = boto3.resource("s3")
_repo_commits_df = []
_repo_pulls_df = []
_repo_pulls_review_df = []
_repo_workflows_df = []
_repo_workflow_runs_df = []


def _start_data_extraction(since=None, until=None):
    """
    :param since: datetime
    :param until: datetime
    :return: None
    """
    print("start")
    org = _get_orgs()
    # check if input since, until would be needed.
    since = datetime.utcnow() - timedelta(days=1)
    until = datetime.utcnow()
    _get_org_members(org)  # 1
    _get_repos(org, since, until)  # 2
    final_commits_df = pd.concat(_repo_commits_df)  # 3
    final_pulls_df = pd.concat(_repo_pulls_df)  # 4
    final_pulls_review_df = pd.concat(_repo_pulls_review_df)  # 5
    final_workflows_df = pd.concat(_repo_workflows_df)  # 6
    final_workflow_run_df = pd.concat(_repo_workflows_df) # 7
    # final_pulls_review_df = pd.concat(_repo_pulls_review_df)
    print(final_commits_df)
    print(final_pulls_df)
    print(final_pulls_review_df)
    print(final_workflows_df)
    print(final_workflow_run_df)


def _get_orgs() -> Organization:
    """
    :rtype: :class:`github.PullRequestComment.PullRequestComment`
    """
    org = [org for org in github.get_user().get_orgs() if org.login == 'gdcorp-dna']
    return org[0]  # only returning org dna for now


def _get_org_members(org: Organization):
    logger.info(f"""Get all members for the org organizations""")
    org_name = org.login
    logger.info(f"getting members for org  {org_name}")
    members = []
    for member in org.get_members():
        member_record = CreateMemberRecord(org_name=org_name, member_id=member.id,
                                           name=member.login, role=member.type, email=member.email,
                                           is_site_admin=member.site_admin, created_at=member.created_at,
                                           updated_at=member.updated_at, etl_load_date=datetime.utcnow())

        members.append(asdict(member_record))
    df = pd.DataFrame.from_records(members)
    print(df)


def _get_repos(org: Organization, since: datetime, until: datetime):
    total_repos = org.get_repos(type='internal').totalCount
    org_name = org.login
    logger.info(f"total repository count in {org_name} is {total_repos}")
    repos = []
    for repo in org.get_repos(type='internal'):
        repository_record = CreateRepositoryRecord(repo.id, org_name, repo.name, repo.description, repo.size
                                                   , repo.default_branch, repo.owner, repo.language, repo.created_at,
                                                   repo.pushed_at, repo.updated_at, datetime.utcnow())
        repos.append(asdict(repository_record))

        # _get_repo_commits(org_name, repo, since, until)
        # _get_repo_pulls(org_name, repo, since, until)
        # _get_repo_pulls_review(org_name, repo, since, until)
        _get_repo_workflow_runs(org_name, repo)
        _get_repo_workflows(org_name=org_name, repo=repo)

        # get Pulls on the repo.

        # select columns and write to S3, check options for overwrite etc.
    df = pd.DataFrame.from_records(repos)

    print(df)  # TODO write to S3


def _get_repo_commits(org_name: str, repo: Repository, since: datetime, until: datetime):
    repo_id = repo.id
    logger.info(f"getting commits for repo {repo.name}")
    commits = []
    try:
        for commit in repo.get_commits(since=since, until=until):
            commit_obj = commit.commit
            num_commit_parents = len(commit.parents)
            num_file_committed = len(commit.files)

            commit_record = CreateCommitRecord(repo_id=repo_id, repo_name=repo.name, github_org=org_name,
                                               commit_sha=commit.sha,
                                               message=commit_obj.message, author_name=commit_obj.author.name,
                                               author_email=commit_obj.author.email,
                                               author_committed_at=commit_obj.author.date,
                                               committer_name=commit_obj.committer.name,
                                               committer_email=commit_obj.committer.email,
                                               committer_committed_at=commit_obj.committer.date,
                                               num_commit_parents=num_commit_parents,
                                               num_file_committed=num_file_committed,
                                               commit_additions=commit.stats.additions,
                                               commit_deletions=commit.stats.deletions,
                                               etl_load_date=datetime.utcnow()
                                               )
            commits.append(asdict(commit_record))
    except GithubException as ge:
        logger.exception(f'error getting the commits for repo id {repo_id} {ge}')

    if len(commits) > 0:
        df = pd.DataFrame.from_records(commits)
        _repo_commits_df.append(df)


def _get_repo_pulls(org_name: str, repo: Repository, since: datetime, until: datetime):
    logger.info(f"getting pulls for repo {repo.name}")
    pulls = []

    for pull in repo.get_pulls():
        if since <= pull.updated_at < until:
            pull_record = CreatePullRecord(org_name=org_name, repo_id=repo.id, repo_name=repo.name, pull_id=pull.id,
                                           pull_number=pull.number, state=pull.state, title=pull.title,
                                           author=pull.user.login, author_id=pull.user.id, body=pull.body,
                                           created_at=pull.created_at, updated_at=pull.updated_at,
                                           closed_at=pull.closed_at, merged_at=pull.merged_at,
                                           is_merged=pull.is_merged(), is_mergeable=pull.mergeable,
                                           mergeable_state=pull.mergeable_state, merged_by=pull.merged_by,
                                           comments=pull.comments, review_comments=pull.review_comments,
                                           commits=pull.commits, additions=pull.additions, deletions=pull.deletions,
                                           changed_files=pull.changed_files, etl_load_date=datetime.utcnow()
                                           )
            pulls.append(asdict(pull_record))

    df = pd.DataFrame.from_records(pulls)
    _repo_pulls_df.append(df)


def _get_repo_pulls_review(org_name: str, repo: Repository, since: datetime, until: datetime):
    logger.info(f"getting reviews for repo {repo.name}")
    pull_reviews = []

    for review in repo.get_pulls_review_comments(since=since):
        if review.updated_at <= until:
            extract_pull_number = urlparse(review.pull_request_url).path.rstrip('/').split('/')[-1]
            pull_number = int(extract_pull_number)

            review_record = CreatePullReviewRecord(org_name=org_name, repo_id=repo.id, repo_name=repo.name,
                                                   pull_request_review_id=review.id,
                                                   pull_request_url=review.pull_request_url, pull_number=pull_number,
                                                   file_path=review.path, original_commit_id=review.original_commit_id,
                                                   review_author=review.user.login, body=review.body,
                                                   created_at=review.created_at, updated_at=review.updated_at,
                                                   etl_load_date=datetime.utcnow()
                                                   )
            pull_reviews.append(asdict(review_record))
    df = pd.DataFrame.from_records(pull_reviews)
    _repo_pulls_review_df.append(df)


def _get_pull_commits():
    pass


def _get_pull_files():
    pass


def _get_repo_workflows(org_name: str, repo: Repository):
    logger.info(f"getting workflows for repo {repo.name}")
    workflows = []

    for workflow in repo.get_workflows():
        workflow_record = CreateWorkflowRecord(org_name=org_name, repo_id=repo.id, repo_name=repo.name,
                                               workflow_id=workflow.id, name=workflow, path=workflow.path,
                                               state=workflow.state, created_at=workflow.created_at,
                                               updated_at=workflow.updated_at, etl_load_date=datetime.utcnow()
                                               )

        workflows.append(asdict(workflow_record))
    df = pd.DataFrame.from_records(workflows)
    _repo_workflows_df.append(df)


def _get_repo_workflow_runs(org_name: str, repo: Repository):
    logger.info(f"getting workflow runs for repo {repo.name}")
    workflow_runs = []

    for workflow_run in repo.get_workflow_runs():
        workflow_run_record = CreateWorkflowRunRecord(org_name=org_name, repo_id=repo.id, repo_name=repo.name,
                                                      workflow_run_id=workflow_run.id, name=workflow_run.name,
                                                      path=workflow_run.path, run_number=workflow_run.run_number,
                                                      head_sha=workflow_run.head_sha,
                                                      head_branch=workflow_run.head_branch,
                                                      event=workflow_run.event, run_attempt=workflow_run.run_attempt,
                                                      status=workflow_run.status, conclusion=workflow_run.conclusion,
                                                      workflow_id=workflow_run.workflow_id,
                                                      workflow_run_url=workflow_run.workflow_run_url,
                                                      actor_name=workflow_run.actor.login,
                                                      triggering_actor_name=workflow_run.triggering_actor.login,
                                                      run_started_at=workflow_run.run_started_at,
                                                      created_at=workflow_run.created_at,
                                                      updated_at=workflow_run.updated_at,
                                                      etl_load_date=datetime.utcnow()
                                                      )

        workflow_runs.append(asdict(workflow_run_record))
    df = pd.DataFrame.from_records(workflow_runs)
    _repo_workflow_runs_df.append(df)


# def _persist_to_s3(dataset_type,  ):
if __name__ == "__main__":
    _start_data_extraction()
