import awswrangler as wr
import pandas as pd
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools import Logger
from github import Github
from github import Organization, Repository
import boto3
from dataclasses import asdict
from datetime import datetime, timedelta

from records import CreateRepositoryRecord, CreateCommitRecord

logger = Logger(service="github_stats")
token = parameters.get_secret("github_auth_token", transform="json")
assert isinstance(token, dict)

github = Github(token["github_pat"])
s3 = boto3.resource("s3")


def main():
    org = _get_orgs()
    since = datetime.utcnow() - timedelta(days=1)
    until = datetime.utcnow()
    _get_repos(org, since, until)


def _start_data_extraction(since, until):
    pass


def _get_orgs() -> Organization:
    org = [org for org in github.get_user().get_orgs() if org.login == 'gdcorp-dna']
    return org[0]  # only returning org dna


def _get_repos(org: Organization, since:datetime, until:datetime):
    total_repos = org.get_repos(type='internal').totalCount
    org_name = org.login
    logger.info(f"total repository count in {org_name} is {total_repos}")
    repos = []
    for repo in org.get_repos(type='internal'):
        repository_record = CreateRepositoryRecord(repo.id, org_name, repo.name, repo.description, repo.size
                                                   , repo.default_branch, repo.owner, repo.language, repo.created_at,
                                                   repo.pushed_at, repo.updated_at, datetime.utcnow())
        repos.append(asdict(repository_record))

        _get_repo_commits(org_name, repo, since, until)

        # get Pulls on the repo.

        # select columns and write to S3, check options for overwrite etc.
    df = pd.DataFrame.from_records(repos)


def _get_repo_commits(org_name: str, repo: Repository, since: datetime, until: datetime):
    repo_id = repo.id
    logger.info(f"getting commits for repo {repo.name}")
    commits = []
    for commit in repo.get_commits(since=since, until=until):
        commit_obj = commit.commit
        num_commit_parents = len(commit.parents)
        num_file_committed = len(commit.files)

        commit_record = CreateCommitRecord(repo_id=repo_id, commit_sha=commit.sha, message=commit_obj.message,
                                           author_name=commit_obj.author.name, author_email=commit_obj.author.email,
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
        commits.append(commit_record)
    df = ''
    if len(commits) >0:
        df = pd.DataFrame.from_dict(commits)
    else:
        logger.info(f"No commits in the given time range from {since} to {until} for repo {repo.name}")
    print(df)


def _get_repo_pulls():
    pass


def _get_pull_commits():
    pass


def _get_pull_files():
    pass


def _get_repo_pulls_comments():
    pass


def _get_repo_pulls_reviews():
    pass


def _get_org_members():
    pass


def _get_repo_workflow():
    pass


def _get_repo_workflow_runs():
    pass


# def _persist_to_s3(dataset_type,  ):
if __name__ == "__main__":
    main()
