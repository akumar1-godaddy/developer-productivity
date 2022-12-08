(
    repo_id UUID NOT NULL,
    commit_hash          TEXT NOT NULL,
    file_path            TEXT NOT NULL,
    additions            INTEGER NOT NULL,
    deletions            INTEGER NOT NULL,
    _mergestat_synced_at TIMESTAMP(6) WITH TIME ZONE DEFAULT now() NOT NULL,
    old_file_mode        TEXT DEFAULT 'unknown'::TEXT NOT NULL,
    new_file_mode        TEXT DEFAULT 'unknown'::TEXT NOT NULL,
-- git commit stats of a repo
