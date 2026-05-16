#!/usr/bin/env bash
# publish-to-git.sh — git-filter-repo wrapper for TOA two-repo distribution
#
# Produces a filtered view of a private TOA-based repo (excluding _proj/)
# and pushes it to a public or client-facing remote, or packages it as a tarball.
#
# Usage:
#   ./publish-to-git.sh init      — interactive first-time setup
#   ./publish-to-git.sh run       — filter + push to configured remote
#   ./publish-to-git.sh package   — filter + produce a tarball (no push)
#   ./publish-to-git.sh status    — show commits since last publish
#   ./publish-to-git.sh help      — show this help
#
# Flags (apply to 'run' and 'package'):
#   --dry-run   Walk through all steps but skip push/write
#
# See docs/guides/publish-setup.md for the full setup guide.

set -euo pipefail

# ---------------------------------------------------------------------------
# Helpers — defined first so they are available to the source guard below
# ---------------------------------------------------------------------------
die() {
    echo "ERROR: $*" >&2
    exit 1
}

info() {
    echo "[publish-to-git] $*"
}

warn() {
    echo "WARNING: $*" >&2
}

# Global temp dir tracker — set by cmd_run and cmd_package, cleaned up by EXIT trap
_PUBLISH_TMP_DIR=""

# Global EXIT trap: remove the temp clone if one was created
_cleanup_tmp() {
    if [ -n "${_PUBLISH_TMP_DIR:-}" ] && [ -d "$_PUBLISH_TMP_DIR" ]; then
        rm -rf "$_PUBLISH_TMP_DIR"
        info "Temp clone cleaned up."
    fi
}
trap '_cleanup_tmp' EXIT

# ---------------------------------------------------------------------------
# Resolve paths relative to the script's own directory
# ---------------------------------------------------------------------------
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_FILE="$SCRIPT_DIR/.publish-config"
LAST_PUBLISH_FILE="$SCRIPT_DIR/.last-publish"

# ---------------------------------------------------------------------------
# Source run-python-tool.sh helper (BL-066 / BL-070)
# Path: _proj/publish_to_git/ is two levels below project root, so
# .claude/scripts/lib/ is at ../../.claude/scripts/lib/ relative to SCRIPT_DIR.
# ---------------------------------------------------------------------------
_RUN_PYTHON_TOOL_LIB="$SCRIPT_DIR/../../.claude/scripts/lib/run-python-tool.sh"
if [ -f "$_RUN_PYTHON_TOOL_LIB" ]; then
    # shellcheck source=../../.claude/scripts/lib/run-python-tool.sh
    source "$_RUN_PYTHON_TOOL_LIB"
else
    die "run-python-tool.sh not found at $_RUN_PYTHON_TOOL_LIB. Re-run install.sh to provision the framework."
fi

# ---------------------------------------------------------------------------
# Defaults (overridable via environment)
# ---------------------------------------------------------------------------
PUBLISH_SRC_BRANCH="${PUBLISH_SRC_BRANCH:-main}"
PUBLISH_FILTER_RULE="${PUBLISH_FILTER_RULE:-_proj/ .claude/}"

usage() {
    cat <<'EOF'
Usage: publish-to-git.sh <command> [flags]

Commands:
  init      Interactive first-time setup (writes .publish-config)
  run       Filter repository and push to configured remote
  package   Filter repository and produce a tarball (no push)
  status    Show commits on private repo since last publish
  help      Show this help message

Flags (for 'run' and 'package'):
  --dry-run   Perform all steps but skip the final push / tarball write

Environment overrides:
  PUBLISH_SRC_BRANCH    Source branch to publish from (default: main)
  PUBLISH_FILTER_RULE   Space-separated paths to exclude (default: _proj/ .claude/)

See docs/guides/publish-setup.md for the full setup guide.
EOF
}

# ---------------------------------------------------------------------------
# Pre-flight: verify working directory is clean
# ---------------------------------------------------------------------------
check_clean_working_tree() {
    # We operate from the repo root (parent of the script dir)
    local repo_root
    repo_root="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" \
        || die "Not inside a git repository. Ensure publish-to-git.sh is run from within a git repo."
    if ! git -C "$repo_root" diff --quiet HEAD 2>/dev/null; then
        die "Working tree has uncommitted changes. Commit or stash before publishing."
    fi
    echo "$repo_root"
}

# ---------------------------------------------------------------------------
# Pre-flight: verify on source branch
# ---------------------------------------------------------------------------
check_source_branch() {
    local repo_root="$1"
    local current_branch
    current_branch="$(git -C "$repo_root" rev-parse --abbrev-ref HEAD 2>/dev/null)" \
        || die "Could not determine current branch."
    if [ "$current_branch" != "$PUBLISH_SRC_BRANCH" ]; then
        die "Currently on branch '$current_branch', expected '$PUBLISH_SRC_BRANCH'. Set PUBLISH_SRC_BRANCH to override."
    fi
}

# ---------------------------------------------------------------------------
# Pre-flight: verify .publish-config exists
# ---------------------------------------------------------------------------
check_config() {
    if [ ! -f "$CONFIG_FILE" ]; then
        die ".publish-config not found. Run '$0 init' first to configure."
    fi
    # Source the config
    # shellcheck source=/dev/null
    source "$CONFIG_FILE"
    : "${PUBLISH_REMOTE:?".publish-config is missing PUBLISH_REMOTE"}"
    : "${PUBLISH_MODE:?".publish-config is missing PUBLISH_MODE"}"
    : "${PUBLISH_BRANCH:?".publish-config is missing PUBLISH_BRANCH"}"
    # Trim whitespace and validate PUBLISH_MODE against the allowlist
    PUBLISH_MODE="${PUBLISH_MODE#"${PUBLISH_MODE%%[![:space:]]*}"}"
    PUBLISH_MODE="${PUBLISH_MODE%"${PUBLISH_MODE##*[![:space:]]}"}"
    case "$PUBLISH_MODE" in
        fresh|resync) ;;
        *) die ".publish-config: PUBLISH_MODE='$PUBLISH_MODE' is invalid. Must be 'fresh' or 'resync'." ;;
    esac
    # Reject empty/whitespace-only filter rule — would otherwise silently publish everything
    if [ -z "${PUBLISH_FILTER_RULE// /}" ]; then
        die ".publish-config: PUBLISH_FILTER_RULE is empty. At least one path must be specified (e.g. PUBLISH_FILTER_RULE=\"_proj/ .claude/\")."
    fi
}

# ---------------------------------------------------------------------------
# Ensure .last-publish is in the repo's .gitignore (.publish-config tracking is a per-repo choice)
# ---------------------------------------------------------------------------
ensure_gitignored() {
    local repo_root="$1"
    local gitignore="$repo_root/.gitignore"
    local added=false

    local comment="# publish-to-git local state (not for commit)"
    local entry="_proj/publish_to_git/.last-publish"
    if ! grep -qxF "$entry" "$gitignore" 2>/dev/null; then
        if [ -s "$gitignore" ] && [ -n "$(tail -c 1 "$gitignore" 2>/dev/null)" ]; then
            echo "" >> "$gitignore"
        fi
        if ! grep -qxF "$comment" "$gitignore" 2>/dev/null; then
            echo "$comment" >> "$gitignore"
        fi
        echo "$entry" >> "$gitignore"
        info "+ .gitignore: added $entry"
        added=true
    fi
    # If the file is currently tracked by git, untrack it so future commits don't capture it.
    if git -C "$repo_root" ls-files --error-unmatch "$entry" > /dev/null 2>&1; then
        git -C "$repo_root" rm --cached "$entry" 2>/dev/null && \
            info "git rm --cached $entry (was tracked; now gitignored)"
    fi
    if [ "$added" = true ]; then
        info ".gitignore updated. Please commit the .gitignore change separately."
    fi
}

# ---------------------------------------------------------------------------
# CMD: init
# ---------------------------------------------------------------------------
cmd_init() {
    if [ ! -t 0 ]; then
        echo "ERROR: 'init' requires an interactive terminal. Run this command directly, not via piped input." >&2
        exit 2
    fi

    local repo_root
    repo_root="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" \
        || die "Not inside a git repository."

    if [ -f "$CONFIG_FILE" ]; then
        echo ""
        echo "A .publish-config already exists at: $CONFIG_FILE"
        printf "Re-configure? [y/N]: "
        read -r reconfigure
        case "$reconfigure" in
            y|Y) ;;
            *) info "Init cancelled — existing config preserved."; exit 0 ;;
        esac
    fi

    echo ""
    echo "=== publish-to-git: first-time setup ==="
    echo ""
    echo "This will create .publish-config in: $SCRIPT_DIR"
    echo "The config file will be gitignored (user-local state)."
    echo ""

    # --- Remote URL ---
    printf "Target remote URL (e.g. git@github.com:user/public-repo.git): "
    read -r input_remote
    [ -n "$input_remote" ] || die "Remote URL cannot be empty."

    # --- Fresh or resync ---
    echo ""
    echo "Is the target a fresh (empty) repo, or does it have existing filtered history?"
    echo "  f) Fresh   — target is empty; first publish creates its history"
    echo "  r) Resync  — target already has history from a previous run"
    echo ""
    printf "Choose [f/r]: "
    read -r input_mode_choice
    case "$input_mode_choice" in
        f|F) input_mode="fresh" ;;
        r|R) input_mode="resync" ;;
        *) die "Invalid choice. Enter 'f' for fresh or 'r' for resync." ;;
    esac

    # --- Branch ---
    echo ""
    printf "Branch to publish to on the public remote [main]: "
    read -r input_branch
    input_branch="${input_branch:-main}"

    # --- Write config ---
    cat > "$CONFIG_FILE" <<EOF
# publish-to-git configuration — DO NOT COMMIT
# Generated by publish-to-git.sh init on $(date -u +"%Y-%m-%dT%H:%M:%SZ")
# Edit manually if needed. Re-run init to regenerate.

PUBLISH_REMOTE="$input_remote"
PUBLISH_MODE="$input_mode"
PUBLISH_BRANCH="$input_branch"
PUBLISH_FILTER_RULE="_proj/ .claude/"
EOF

    info "Configuration written to: $CONFIG_FILE"
    ensure_gitignored "$repo_root"
    echo ""
    echo "Setup complete. Run '$0 run' when ready to publish."
    echo "On first publish with PUBLISH_MODE=fresh, the target remote must be empty."
}

# ---------------------------------------------------------------------------
# CMD: run  (filter + push)
# ---------------------------------------------------------------------------
cmd_run() {
    local dry_run="$1"   # "true" or "false"

    local repo_root
    repo_root="$(check_clean_working_tree)"
    check_source_branch "$repo_root"
    check_config   # sources .publish-config, sets PUBLISH_REMOTE, PUBLISH_MODE, PUBLISH_BRANCH

    local src_sha
    src_sha="$(git -C "$repo_root" rev-parse HEAD)"

    info "Source repo : $repo_root"
    info "Source SHA  : $src_sha"
    info "Filter rule : exclude $PUBLISH_FILTER_RULE"
    info "Target remote: $PUBLISH_REMOTE"
    info "Target branch: $PUBLISH_BRANCH"
    info "Mode        : $PUBLISH_MODE"
    [ "$dry_run" = "true" ] && info "DRY RUN — push will be skipped"
    echo ""

    # --- Create temp clone ---
    _PUBLISH_TMP_DIR="$(mktemp -d /tmp/toa-publish-$$-XXXXXX)"
    info "Creating temp clone at: $_PUBLISH_TMP_DIR"

    git clone --no-local -- "$repo_root" "$_PUBLISH_TMP_DIR"
    info "Temp clone created."

    # --- Run git-filter-repo on temp clone ---
    filter_args=()
    # shellcheck disable=SC2086
    for p in $PUBLISH_FILTER_RULE; do
        filter_args+=(--path "$p")
    done
    info "Running git-filter-repo (invert-paths ${filter_args[*]}) ..."
    run_python_tool git-filter-repo \
        --invert-paths \
        "${filter_args[@]}" \
        --force \
        --source "$_PUBLISH_TMP_DIR" \
        --target "$_PUBLISH_TMP_DIR"

    info "Filter complete."

    # --- Push to remote ---
    local push_flag=""
    if [ "$PUBLISH_MODE" = "resync" ]; then
        # Resync: force-push is expected because history was rewritten.
        # Safety: confirm before forcing to the target branch.
        if [ "$dry_run" = "false" ]; then
            echo ""
            warn "RESYNC MODE: This will force-push to '$PUBLISH_BRANCH' on '$PUBLISH_REMOTE'."
            warn "This rewrites history on the public remote. Ensure you own that remote."
            printf "Proceed? [yes/N]: "
            read -r confirm_push
            [ "$confirm_push" = "yes" ] || { info "Push cancelled by user."; exit 0; }
        fi
        push_flag="--force"
    fi

    if [ "$dry_run" = "true" ]; then
        info "DRY RUN: Would push to $PUBLISH_REMOTE $PUBLISH_BRANCH $push_flag"
        info "DRY RUN: Skipping push."
    else
        info "Pushing to $PUBLISH_REMOTE ..."
        git -C "$_PUBLISH_TMP_DIR" remote add publish-target "$PUBLISH_REMOTE"
        # SC2086: push_flag intentionally unquoted to allow empty-string expansion
        # shellcheck disable=SC2086
        git -C "$_PUBLISH_TMP_DIR" push $push_flag publish-target "HEAD:$PUBLISH_BRANCH"
        info "Push complete."
    fi

    # --- Record last-publish SHA ---
    if [ "$dry_run" = "false" ]; then
        echo "$src_sha" > "$LAST_PUBLISH_FILE"
        info "Last-publish SHA recorded: $src_sha"
    fi

    echo ""
    info "Done."
}

# ---------------------------------------------------------------------------
# CMD: package  (filter + tarball, no push)
# ---------------------------------------------------------------------------
cmd_package() {
    local dry_run="$1"

    local repo_root
    repo_root="$(check_clean_working_tree)"
    check_source_branch "$repo_root"
    # Config is optional for package — we just need the filter rule
    if [ -f "$CONFIG_FILE" ]; then
        # shellcheck source=/dev/null
        source "$CONFIG_FILE"
    fi
    # Reject empty/whitespace-only filter rule — would otherwise silently publish everything
    if [ -z "${PUBLISH_FILTER_RULE// /}" ]; then
        die ".publish-config: PUBLISH_FILTER_RULE is empty. At least one path must be specified (e.g. PUBLISH_FILTER_RULE=\"_proj/ .claude/\")."
    fi

    local src_sha
    src_sha="$(git -C "$repo_root" rev-parse HEAD)"
    local repo_basename
    repo_basename="$(basename "$repo_root")"
    local tarball_path
    tarball_path="$(dirname "$repo_root")/${repo_basename}-public-$(date +%Y%m%d).tar.gz"

    info "Source repo    : $repo_root"
    info "Source SHA     : $src_sha"
    info "Filter rule    : exclude $PUBLISH_FILTER_RULE"
    info "Output tarball : $tarball_path"
    [ "$dry_run" = "true" ] && info "DRY RUN — tarball will not be written"
    echo ""

    _PUBLISH_TMP_DIR="$(mktemp -d /tmp/toa-publish-$$-XXXXXX)"
    info "Creating temp clone at: $_PUBLISH_TMP_DIR"

    git clone --no-local -- "$repo_root" "$_PUBLISH_TMP_DIR"
    info "Temp clone created."

    filter_args=()
    # shellcheck disable=SC2086
    for p in $PUBLISH_FILTER_RULE; do
        filter_args+=(--path "$p")
    done
    info "Running git-filter-repo (invert-paths ${filter_args[*]}) ..."
    run_python_tool git-filter-repo \
        --invert-paths \
        "${filter_args[@]}" \
        --force \
        --source "$_PUBLISH_TMP_DIR" \
        --target "$_PUBLISH_TMP_DIR"
    info "Filter complete."

    if [ "$dry_run" = "true" ]; then
        info "DRY RUN: Would create tarball at: $tarball_path"
        info "DRY RUN: Skipping tarball creation."
    else
        info "Creating tarball..."
        # Archive the working tree (not .git) for a clean distribution package
        git -C "$_PUBLISH_TMP_DIR" archive --format=tar.gz --prefix="${repo_basename}-public/" HEAD \
            > "$tarball_path"
        info "Tarball created: $tarball_path"
        info "Size: $(du -sh "$tarball_path" | cut -f1)"
    fi

    echo ""
    info "Done."
}

# ---------------------------------------------------------------------------
# CMD: status
# ---------------------------------------------------------------------------
cmd_status() {
    local repo_root
    repo_root="$(git -C "$SCRIPT_DIR" rev-parse --show-toplevel 2>/dev/null)" \
        || die "Not inside a git repository."

    if [ ! -f "$LAST_PUBLISH_FILE" ]; then
        info "No last-publish record found. Run '$0 run' first."
        exit 0
    fi

    local last_sha
    last_sha="$(cat "$LAST_PUBLISH_FILE")"
    info "Last published SHA: $last_sha"

    local commit_count
    commit_count="$(git -C "$repo_root" rev-list "${last_sha}..HEAD" --count 2>/dev/null)" || {
        warn "Could not compute commit range. The last-publish SHA may no longer be in history."
        commit_count="unknown"
    }

    if [ "$commit_count" = "0" ] || [ "$commit_count" = "unknown" ]; then
        info "Commits since last publish: $commit_count"
    else
        info "$commit_count commit(s) on private since last publish:"
        echo ""
        git -C "$repo_root" log "${last_sha}..HEAD" --oneline
        echo ""
        info "Run '$0 run' to publish these commits."
    fi
}

# ---------------------------------------------------------------------------
# Main: parse command and flags
# ---------------------------------------------------------------------------
COMMAND="${1:-help}"
DRY_RUN="false"

# Shift past command
shift 2>/dev/null || true

# Parse remaining flags
while [ $# -gt 0 ]; do
    case "$1" in
        --dry-run) DRY_RUN="true" ;;
        *) die "Unknown flag: $1. Run '$0 help' for usage." ;;
    esac
    shift
done

case "$COMMAND" in
    init)    cmd_init ;;
    run)     cmd_run "$DRY_RUN" ;;
    package) cmd_package "$DRY_RUN" ;;
    status)  cmd_status ;;
    help|-h|--help) usage ;;
    *) die "Unknown command: '$COMMAND'. Run '$0 help' for usage." ;;
esac
