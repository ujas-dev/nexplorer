# 🚀 How to Publish NexPlorer on GitHub (Zero Local Setup)

## Step 1 — Create the GitHub Repository

1. Go to **github.com** → click **"+"** → **"New repository"**
2. Name: `nexplorer`
3. Description: `Intelligent cross-platform file explorer — no installation required`
4. Visibility: **Public** ← REQUIRED for unlimited free Actions minutes
5. **Do NOT** initialize with README (we already have one)
6. Click **"Create repository"**

---

## Step 2 — Push Code to GitHub

In your terminal or VS Code devcontainer:

```bash
cd /workspace   # your project root

# Initialize git
git init
git branch -M main

# Stage everything
git add .
git commit -m "feat: initial release NexPlorer v1.0.0"

# Connect to GitHub
git remote add origin https://github.com/ujas-dev/nexplorer.git

# Push
git push -u origin main
```

---

## Step 3 — Create a Release (this triggers the build)

1. Go to your repo on GitHub
2. Right side panel → click **"Releases"**
3. Click **"Draft a new release"**
4. Click **"Choose a tag"** → type `v1.0.0` → click **"Create new tag: v1.0.0"**
5. Title: `NexPlorer v1.0.0 — Initial Release`
6. Description: paste from CHANGELOG.md
7. Click **"Publish release"** ← this triggers the workflow

---

## Step 4 — Watch the Build

1. Go to your repo → **"Actions"** tab
2. You'll see **"Build & Release"** workflow running
3. 3 parallel jobs: Windows + Linux + macOS
4. Each takes ~15–20 minutes (Nuitka compiles Python → C → binary)
5. When all 3 complete ✅:

---

## Step 5 — Download Executables

Go to **"Releases"** → `v1.0.0` — you'll see:

```
Assets
  NexPlorer-windows-x86_64.exe    ~30 MB
  NexPlorer-linux-x86_64          ~22 MB
  NexPlorer-macos-x86_64          ~28 MB
  Source code (zip)
  Source code (tar.gz)
```

**These are the portable standalone executables. No Python needed.**

---

## Free Plan Limits (Public Repo)

| Resource | Free limit | NexPlorer usage per release |
|---|---|---|
| Actions minutes | **Unlimited** (public repo) | ~45-60 min (3 × 15-20 min) |
| Storage (artifacts) | 500 MB | ~80 MB per release |
| Concurrent jobs | 20 | 3 |

**Cost: $0.00** — public repos have unlimited free minutes [web:252][web:258].

---

## How to Release v1.0.1 (future updates)

```bash
# Make changes, commit, push
git add .
git commit -m "fix: your bug fix"
git push

# Create new release on GitHub → tag v1.0.1 → Publish
# → Workflow runs automatically → new executables appear
```

**You never need to run anything locally. GitHub builds everything.**
