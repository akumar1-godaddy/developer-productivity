from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class CreateRepositoryRecord:
    __slots__ = ['repo_id', 'github_org', 'repo_name', 'description', 'size', 'default_branch',
                 'owner_name', 'primary_language', 'created_at', 'pushed_at', 'updated_at', 'etl_load_date']
    repo_id: int
    github_org: str
    repo_name: str
    description: str
    size: int
    default_branch: str
    owner_name: str
    primary_language: str
    created_at: datetime
    pushed_at: datetime
    updated_at: datetime
    etl_load_date: datetime


@dataclass(frozen=True)
class CreateCommitRecord:
    __slots__ = ['repo_id', 'repo_name', 'github_org', 'commit_sha', 'message', 'author_name', 'author_email', 'author_committed_at',
                 'committer_name', 'committer_email', 'committer_committed_at', 'commit_parents', 'num_commit_parents',
                 'num_file_committed', 'commit_additions', 'commit_deletions', 'etl_load_date']
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
    etl_load_date: datetime


@dataclass(frozen=True)
class CreateMemberRecord:
    __slots__ = ['org_name', 'member_id', 'name', 'role', 'email', 'is_site_admin',
                 'created_at', 'updated_at', 'etl_load_date']
    org_name: str
    member_id: str
    name: str
    role: str
    email: str
    is_site_admin: bool
    created_at: datetime
    updated_at: datetime
    etl_load_date: datetime


@dataclass(frozen=True)
class CreatePullRecord:
    __slots__ = ['org_name', 'repo_id', 'repo_name', 'pull_id', 'pull_number', 'state', 'title', 'author', 'author_id',
                 'body', 'created_at', 'updated_at', 'closed_at', 'merged_at', 'is_merged', 'is_mergeable',
                 'mergeable_state', 'merged_by', 'comments', 'review_comments', 'commits', 'additions', 'deletions',
                 'changed_files', 'etl_load_date']
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
    comments: int
    review_comments: int
    commits: int
    additions: int
    deletions: int
    changed_files: int
    etl_load_date: datetime


@dataclass(frozen=True)
class CreatePullReviewRecord:
    __slots__ = ['org_name', 'repo_id', 'repo_name', 'pull_request_review_id', 'pull_id', 'pull_number', 'path',
                 'original_commit_id', 'reviewed_by',
                 'body', 'created_at', 'updated_at', 'author_association', 'etl_load_date']
    org_name: str
    repo_id: int
    repo_name: str
    pull_request_review_id: int
    pull_id: int
    pull_number: int
    path: str
    original_commit_id: str
    reviewed_by: str
    body: str
    created_at: datetime
    updated_at: datetime
    author_association: str
    etl_load_date: datetime
