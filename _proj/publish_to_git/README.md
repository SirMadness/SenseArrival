# publish-to-git

A thin wrapper over [`git-filter-repo`](https://github.com/newren/git-filter-repo) that produces a filtered view of a private TOA-based repository by excluding `_proj/` and `.claude/` (and any additional paths you configure), then pushes it to a public or client-facing remote (or packages it as a tarball for offline delivery).

## Quick start

```bash
# One-time setup
cd _proj/publish_to_git
./publish-to-git.sh init

# Publish
./publish-to-git.sh run

# Check what would be published
./publish-to-git.sh status

# Package as tarball (offline / client delivery)
./publish-to-git.sh package
```

## Commands

| Command | Description |
|---------|-------------|
| `init` | Interactive first-time setup; writes `.publish-config` |
| `run` | Filter repo and push to configured remote |
| `package` | Filter repo and produce a tarball; no push |
| `status` | Show commits since last publish |
| `help` | Show usage |

All commands accept `--dry-run` to walk through steps without pushing or writing.

## How it works

1. Makes a disposable clone of the private repo (never touches your working directory).
2. Runs `git-filter-repo --invert-paths --path _proj/ --path .claude/` on the clone to strip all excluded content from every commit. Multiple paths are supported via space-separated values in `PUBLISH_FILTER_RULE`; `.claude/` is excluded by default alongside `_proj/`.
3. Pushes the filtered clone to the configured public remote (`run`) or archives it as a tarball (`package`).

Re-syncs are safe: because `git-filter-repo` deterministically rewrites history, running it twice against the same source produces identical commit hashes for unchanged history. A force-push on resync replaces the public remote's history with the deterministically re-filtered private history — no duplicate commits.

## Local state files

| File | Purpose |
|------|---------|
| `.publish-config` | Your remote URL, mode, and filter rule; tracking is a per-repo choice (this repo tracks it; per-dev setups should add it to .gitignore manually) |
| `.last-publish` | SHA of last published commit; used by `status`; gitignored |

Both files are automatically added to `.gitignore` during `init`.

## Full setup guide

See [`docs/guides/publish-setup.md`](../../docs/guides/publish-setup.md) for prerequisites, first-publish walkthrough, re-sync behavior, tarball mode, FAQ, and troubleshooting.
