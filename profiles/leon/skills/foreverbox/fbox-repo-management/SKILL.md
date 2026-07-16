---
name: fbox-repo-management
description: "Clone/create/fork repos; manage remotes, releases. Auto-commit with detailed messages generated from git diff."
version: 1.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [GitHub, Repositories, Git, Releases, Secrets, Configuration]
    related_skills: [github-auth, github-pr-workflow, github-issues]
---

# Foreverbox Repository Management

Create, clone, fork, configure, and manage GitHub repositories within the Foreverbox ecosystem. Each section shows `gh` first, then the `git` + `curl` fallback.

## Prerequisites

- Authenticated with GitHub (see `github-auth` skill)

### Repo Registry

Map human-readable repo names to their local paths. Extend this list when new repos join the ecosystem.

| Name | Local path | Remote |
|------|-----------|--------|
| `council-library` | `/foreverbox_data/council-library` | `github.com/quiddity-sea/council-library` (private) |

### Usage pattern

When the user says "commit to the council-library" or "push the changes":
1. Look up the repo name in the registry above
2. `cd` to the local path
3. Follow the Commit & Push workflow below

---

## 1. Auto-Commit & Push

**Trigger:** User says "commit to [repo-name]" or "push [repo-name]". Look up the repo in the registry, navigate to it, and follow this workflow.

### Step 1: Assess changes

```bash
cd <repo-path-from-registry>
git fetch origin
git status
git diff --stat
git log --oneline -1
```

### Step 2: Review the full diff

```bash
git diff HEAD
```

Read the output carefully. Every file change must be understood and reflected in the commit message.

### Step 3: Build a detailed commit message

Structure:

```
<type>: <concise subject — 50-72 chars, imperative, lowercase, no period>

<body — grouped by logical change, not per-file>

- Area 1: what changed and why
- Area 2: what changed and why
```

**Types:** `feat`, `fix`, `refactor`, `docs`, `chore`, `perf`, `test`

**Rules:**
- Group related file changes under one bullet, not one bullet per file
- New files: mention them explicitly
- Renamed files: note old→new
- Deleted files: explain why
- Docs archived/versioned: note the convention applied

### Step 4: Commit and push

```bash
git add -A
git commit -m "$MESSAGE"
git push origin main
```

### Anti-patterns

- **NEVER** `git commit -am "updated files"` — always generate a detailed message from `git diff`
- **NEVER** skip `git fetch` — stale local state causes push rejections
- **NEVER** commit without reviewing `git diff HEAD` first — message must reflect actual changes
- **NEVER** push unless the user explicitly asked you to push

---

### Setup (auth detection)

```bash
if command -v gh &>/dev/null && gh auth status &>/dev/null; then
  AUTH="gh"
else
  AUTH="git"
  if [ -z "$GITHUB_TOKEN" ]; then
    if _hermes_env="${HERMES_HOME:-$HOME/.hermes}/.env"; [ -f "$_hermes_env" ] && grep -q "^GITHUB_TOKEN=" "$_hermes_env"; then
      GITHUB_TOKEN=$(grep "^GITHUB_TOKEN=" "$_hermes_env" | head -1 | cut -d= -f2 | tr -d '\n\r')
    elif grep -q "github.com" ~/.git-credentials 2>/dev/null; then
      GITHUB_TOKEN=$(grep "github.com" ~/.git-credentials 2>/dev/null | head -1 | sed 's|https://[^:]*:\([^@]*\)@.*|\\1|')
    fi
  fi
fi

# Get your GitHub username (needed for several operations)
if [ "$AUTH" = "gh" ]; then
  GH_USER=$(gh api user --jq '.login')
else
  GH_USER=$(curl -s -H "Authorization: token $GITHUB_TOKEN" https://api.github.com/user | python3 -c "import sys,json; print(json.load(sys.stdin)['login'])")
fi
```

If you're inside a repo already:

```bash
REMOTE_URL=$(git remote get-url origin)
OWNER_REPO=$(echo "$REMOTE_URL" | sed -E 's|.*github\.com[:/]||; s|\.git$||')
OWNER=$(echo "$OWNER_REPO" | cut -d/ -f1)
REPO=$(echo "$OWNER_REPO" | cut -d/ -f2)
```

---

## 2. Cloning Repositories

Cloning is pure `git` — works identically either way:

```bash
git clone https://github.com/owner/repo-name.git
git clone https://github.com/owner/repo-name.git ./my-local-dir
git clone --depth 1 https://github.com/owner/repo-name.git
git clone --branch develop https://github.com/owner/repo-name.git
git clone git@github.com:owner/repo-name.git
```

**With gh (shorthand):**

```bash
gh repo clone owner/repo-name
gh repo clone owner/repo-name -- --depth 1
```

## 3. Creating Repositories

**With gh:**

```bash
gh repo create my-new-project --public --clone
gh repo create my-new-project --private --description "A useful tool" --license MIT --clone
gh repo create my-org/my-new-project --public --clone
cd /path/to/existing/project
gh repo create my-project --source . --public --push
```

**With git + curl:**

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user/repos \
  -d '{"name": "my-new-project", "description": "A useful tool", "private": false, "auto_init": true, "license_template": "mit"}'

git clone https://github.com/$GH_USER/my-new-project.git
cd my-new-project

# -- OR -- push existing directory
cd /path/to/existing/project
git init && git add . && git commit -m "Initial commit"
git remote add origin https://github.com/$GH_USER/my-new-project.git
git push -u origin main
```

## 4. Forking Repositories

```bash
gh repo fork owner/repo-name --clone
```

**With git + curl:**

```bash
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/repos/owner/repo-name/forks

sleep 3
git clone https://github.com/$GH_USER/repo-name.git
cd repo-name
git remote add upstream https://github.com/owner/repo-name.git
```

## 5. Repository Information

```bash
gh repo view owner/repo-name
gh repo list --limit 20
```

## 6. Repository Settings

```bash
gh repo edit --description "Updated description" --visibility public
gh repo edit --enable-wiki=false --enable-issues=true
```

## 7. Releases

```bash
gh release create v1.0.0 --title "v1.0.0" --generate-notes
gh release list
```

## Quick Reference Table

| Action | gh | git + curl |
|--------|-----|-----------|
| Commit & push | `git add -A && git commit -m "..." && git push` | Same |
| Clone | `gh repo clone o/r` | `git clone https://github.com/o/r.git` |
| Create repo | `gh repo create name --public` | `curl POST /user/repos` |
| Fork | `gh repo fork o/r --clone` | `curl POST /repos/o/r/forks` + `git clone` |
| Repo info | `gh repo view o/r` | `curl GET /repos/o/r` |
| Create release | `gh release create v1.0` | `curl POST /repos/o/r/releases` |
