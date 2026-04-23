#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")" && pwd)"
TARGET_DIR="$HOME/.hermes/skills/productivity/portfolio-ledger"

mkdir -p "$TARGET_DIR"
cp "$REPO_ROOT/SKILL.md" "$TARGET_DIR/SKILL.md"

printf '%s\n' "Installed Hermes skill prompt to: $TARGET_DIR/SKILL.md"
printf '%s\n' ""
printf '%s\n' "This repository remains the runnable implementation."
printf '%s\n' "Use Hermes from this repo directory, or point the skill to this repo clone."
printf '%s\n' ""
printf '%s\n' "Recommended next steps:"
printf '%s\n' "  1. cd $REPO_ROOT"
printf '%s\n' "  2. hermes chat -s portfolio-ledger"
