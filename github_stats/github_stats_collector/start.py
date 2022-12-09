import awswrangler as wr
import pandas as pd
from aws_lambda_powertools.utilities import parameters
from aws_lambda_powertools import Logger
from github import Github
from github import Organization, Repository, GithubException
import boto3
from dataclasses import asdict
from datetime import datetime, timedelta

from records import CreateRepositoryRecord, CreateCommitRecord, CreateMemberRecord, CreatePullRecord, \
    CreatePullReviewRecord

logger = Logger(service="github_stats")
token = parameters.get_secret("github_auth_token", transform="json")
assert isinstance(token, dict)

github = Github(token["github_pat"])
s3 = boto3.resource("s3")
commits_df = []
pulls_df = []

def main():
    org = _get_orgs()
    since = datetime.utcnow() - timedelta(days=1)
    until = datetime.utcnow()
    _get_repos(org, since, until)
    final_commits_df = pd.concat(commits_df)
    final_pulls_df = pd.concat(pulls_df)
    print(final_commits_df)
    print(final_pulls_df)
    _get_org_members(org)


def _start_data_extraction(since, until):
    pass


def _get_orgs() -> Organization:
    org = [org for org in github.get_user().get_orgs() if org.login == 'gdcorp-dna']
    return org[0]  # only returning org dna


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

        _get_repo_commits(org_name, repo, since, until)
        _get_repo_pulls(org_name, repo, since, until)
        _get_repo_pulls_review(org_name, repo, since, until)

        # get Pulls on the repo.

        # select columns and write to S3, check options for overwrite etc.
    df = pd.DataFrame.from_records(repos)

    print(df)


def _get_repo_commits(org_name: str, repo: Repository, since: datetime, until: datetime):
    repo_id = repo.id
    logger.info(f"getting commits for repo {repo.name}")
    commits = []
    try:
        for commit in repo.get_commits(since=since, until=until):
            commit_obj = commit.commit
            num_commit_parents = len(commit.parents)
            num_file_committed = len(commit.files)

            commit_record = CreateCommitRecord(repo_id=repo_id,repo_name=repo.name, github_org=org_name,
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
        commits_df.append(df)


def _get_repo_pulls(org_name: str, repo: Repository, since: datetime, until: datetime):
    logger.info(f"getting pulls for repo {repo.name}")
    pulls = []

    for pull in repo.get_pulls():
        if pull.updated_at >= since and pull.updated_at < until:
            pull_record = CreatePullRecord(org_name=org_name, repo_id=repo.id, repo_name=repo.name, pull_id= pull.id,
                                           pull_number=pull.number, state=pull.state, title=pull.title,
                                           author=pull.user.login, author_id=pull.user.id, body=pull.body,
                                           created_at=pull.created_at, updated_at=pull.updated_at,
                                           closed_at=pull.closed_at, merged_at=pull.merged_at,
                                           is_merged=pull.is_merged(), is_mergeable=pull.mergeable,
                                           mergeable_state=pull.mergeable_state, merged_by= pull.merged_by,
                                           comments=pull.comments, review_comments= pull.review_comments,
                                           commits=pull.commits, additions=pull.additions, deletions= pull.deletions,
                                           changed_files=pull.changed_files, etl_load_date=datetime.utcnow()
                                           )
            pulls.append(asdict(pull_record))

    df = pd.DataFrame.from_records(pulls)
    pulls_df.append(df)


def _get_repo_pulls_review(org_name: str, repo: Repository, since: datetime, until: datetime):

    logger.info(f"getting reviews for repo {repo.name}")
    reviews = []
    for review in repo.get_pulls_review_comments(since, until):


        review_record = CreatePullReviewRecord(org_name=org_name, repo_id=repo.id, repo_name=repo.name,

                                               pull_number=r.number, state=pull.state, title=pull.title,
                                               author=pull.user.login, author_id=pull.user.id, body=pull.body,
                                               created_at=pull.created_at, updated_at=pull.updated_at,
                                               closed_at=pull.closed_at, merged_at=pull.merged_at,
                                               is_merged=pull.is_merged(), is_mergeable=pull.mergeable,
                                               mergeable_state=pull.mergeable_state, merged_by= pull.merged_by,
                                               comments=pull.comments, review_comments= pull.review_comments,
                                               commits=pull.commits, additions=pull.additions, deletions= pull.deletions,
                                               changed_files=pull.changed_files, etl_load_date=datetime.utcnow()
                                               )




def _get_org_members(org: Organization):
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


def _get_pull_commits():
    pass


def _get_pull_files():
    pass



def _get_repo_workflow():
    pass


def _get_repo_workflow_runs():
    pass


# def _persist_to_s3(dataset_type,  ):
if __name__ == "__main__":
    main()
