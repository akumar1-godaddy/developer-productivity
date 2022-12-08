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
    __slots__ = ['repo_id', 'commit_sha', 'message', 'author_name', 'author_email', 'author_committed_at',
                 'committer_name', 'committer_email', 'committer_committed_at', 'commit_parents', 'num_commit_parents',
                 'num_file_committed', 'commit_additions', 'commit_deletions', 'etl_load_date']
    repo_id: int
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
