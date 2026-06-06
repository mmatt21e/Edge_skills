#!/usr/bin/env bash
# Collect non-merge commits in a range as "subject<TAB>shorthash" lines.
# Usage: collect.sh [<from-ref>] [<to-ref>]
#   from defaults to the most recent tag (or the root commit if no tags exist)
#   to   defaults to HEAD
set -euo pipefail

to="${2:-HEAD}"

if [ -n "${1:-}" ]; then
  from="$1"
else
  if from="$(git describe --tags --abbrev=0 2>/dev/null)"; then
    : # use latest tag
  else
    from="$(git rev-list --max-parents=0 HEAD | tail -n 1)" # root commit
  fi
fi

git log --no-merges --pretty=format:'%s%x09%h' "${from}..${to}"
