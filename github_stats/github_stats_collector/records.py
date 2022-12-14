from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CreateRepositoryRecord:
    __slots__ = ['repo_id', 'org_name', 'repo_name', 'description', 'size', 'default_branch',
                 'owner_name', 'primary_language', 'created_at', 'pushed_at', 'updated_at', 'etl_load_utc_timestamp']
    repo_id: int
    org_name: str
    repo_name: str
    description: str
    size: int
    default_branch: str
    owner_name: str
    primary_language: str
    created_at: datetime
    pushed_at: datetime
    updated_at: datetime
    etl_load_utc_timestamp: datetime


@dataclass(frozen=True)
class CreateCommitRecord:
    __slots__ = ['repo_id', 'repo_name', 'github_org', 'commit_sha', 'message', 'author_name', 'author_email',
                 'author_committed_at',
                 'committer_name', 'committer_email', 'committer_committed_at', 'num_commit_parents',
                 'num_file_committed', 'commit_additions', 'commit_deletions', 'etl_load_utc_timestamp']
    repo_id: int
    repo_name: str
    github_org: str
    commit_sha: str
    message: str
    author_name: str
    author_email: int
    author_committed_at: datetime
    committer_name: str
    committer_email: str
    committer_committed_at: datetime
    num_commit_parents: int
    num_file_committed: int
    commit_additions: int
    commit_deletions: int
    etl_load_utc_timestamp: datetime


@dataclass(frozen=True)
class CreateMemberRecord:
    __slots__ = ['org_name', 'member_id', 'name', 'role', 'email', 'is_site_admin',
                 'created_at', 'updated_at', 'etl_load_utc_timestamp']
    org_name: str
    member_id: int
    name: str
    role: str
    email: str
    is_site_admin: bool
    created_at: datetime
    updated_at: datetime
    etl_load_utc_timestamp: datetime


@dataclass(frozen=True)
class CreatePullRecord:
    __slots__ = ['org_name', 'repo_id', 'repo_name', 'pull_id', 'pull_number', 'state', 'title', 'author', 'author_id',
                 'body', 'created_at', 'updated_at', 'closed_at', 'merged_at', 'is_merged', 'is_mergeable',
                 'mergeable_state', 'merged_by', 'comments_cnt', 'review_comments_cnt', 'commits', 'additions', 'deletions',
                 'changed_files', 'etl_load_utc_timestamp']
    org_name: str
    repo_id: int
    repo_name: str
    pull_id: int
    pull_number: int
    state: str
    title: str
    author: str
    author_id: int
    body: str
    created_at: datetime
    updated_at: datetime
    closed_at: datetime
    merged_at: datetime
    is_merged: bool
    is_mergeable: bool
    mergeable_state: str
    merged_by: str
    comments_cnt: int
    review_comments_cnt: int
    commits: int
    additions: int
    deletions: int
    changed_files: int
    etl_load_utc_timestamp: datetime


@dataclass(frozen=True)
# "Pull Request Review Comment"
# "Pull Request Review Comments are comments_cnt on a portion of the Pull Request's diff."
class CreatePullReviewRecord:
    __slots__ = ['org_name', 'repo_id', 'repo_name', 'pull_request_review_id', 'pull_request_url', 'pull_number',
                 'file_path', 'original_commit_id', 'review_author',  # 'author_association',
                 'body', 'created_at', 'updated_at', 'etl_load_utc_timestamp']
    org_name: str
    repo_id: int
    repo_name: str
    # "The ID of the pull request review to which the comment belongs."
    pull_request_review_id: int
    pull_request_url: str
    pull_number: int
    "The relative path of the file to which the comment applies."
    file_path: str
    original_commit_id: str
    review_author: str
    # author_association: str  # this is also not available
    # "The text of the comment."
    body: str
    created_at: datetime
    updated_at: datetime
    etl_load_utc_timestamp: datetime


# Where to get the comment count, do we need it ready made or can it be queried


@dataclass(frozen=True)
class CreateWorkflowRunRecord:
    __slots__ = ['org_name', 'repo_id', 'repo_name', 'workflow_run_id', 'head_branch',
                 'head_sha',  'run_number', 'run_attempt', 'event', 'status', 'conclusion', 'workflow_id',
                 'workflow_run_url',  'run_started_at', 'created_at', 'updated_at',
                 'etl_load_utc_timestamp']
    org_name: str
    repo_id: int
    repo_name: str
    workflow_run_id: int
    head_branch: str
    head_sha: str
    run_number: int
    run_attempt: int
    event: str
    status: str
    conclusion: str
    workflow_id: int
    workflow_run_url: str
    # actor_name: str
    # triggering_actor_name: str
    run_started_at: datetime
    created_at: datetime
    updated_at: datetime
    etl_load_utc_timestamp: datetime


@dataclass(frozen=True)
class CreateWorkflowRecord:
    __slots__ = ['org_name', 'repo_id', 'repo_name', 'workflow_id', 'name', 'path', 'state', 'created_at', 'updated_at',
                 'etl_load_utc_timestamp']
    org_name: str
    repo_id: int
    repo_name: str
    workflow_id: int
    name: str
    path: str
    state: str
    created_at: datetime
    updated_at: datetime
    etl_load_utc_timestamp: datetime
