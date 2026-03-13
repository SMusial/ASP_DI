# Version Control Guide for ASP_DI Project

## Option 1: Git Version Control (Recommended)

### Initial Setup

```bash
cd /mnt/c/Users/EPOSYMU/python/kiro/ASP_DI

# Initialize git repository
git init

# Create .gitignore file
cat > .gitignore << EOF
# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
venv/
env/

# PyTensor cache
.pytensor/

# Streamlit
.streamlit/

# Data (optional - uncomment if you want to track data)
# data/*.csv
# data/*.json

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF

# Add all files
git add .

# Create initial commit
git commit -m "Initial commit: Bayesian Analytics Module 1"
```

### Creating Version Snapshots

```bash
# After making changes, create a new version
git add .
git commit -m "Enhanced: Added Bayesian vs Simple Average comparison"

# Tag important versions
git tag -a v1.0 -m "Version 1.0: Basic Bayesian Analytics"
git tag -a v1.1 -m "Version 1.1: Added continuous learning simulator"
git tag -a v1.2 -m "Version 1.2: Added posterior distributions"
```

### Viewing Version History

```bash
# See all commits
git log --oneline

# See all tags
git tag -l

# Compare versions
git diff v1.0 v1.1
```

### Restoring Previous Versions

```bash
# View a specific version (read-only)
git checkout v1.0

# Return to latest
git checkout main

# Create a branch from old version
git checkout -b feature-from-v1.0 v1.0
```

---

## Option 2: Manual Backup with Timestamps

### Create Backup Script

```bash
# Create backup script
cat > backup_version.sh << 'EOF'
#!/bin/bash

# Get current date and time
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_DIR="../ASP_DI_backups"
BACKUP_NAME="ASP_DI_${TIMESTAMP}"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Copy entire project
cp -r . "$BACKUP_DIR/$BACKUP_NAME"

# Exclude venv and cache
rm -rf "$BACKUP_DIR/$BACKUP_NAME/venv"
rm -rf "$BACKUP_DIR/$BACKUP_NAME/__pycache__"
rm -rf "$BACKUP_DIR/$BACKUP_NAME"/*/__pycache__

echo "Backup created: $BACKUP_DIR/$BACKUP_NAME"
EOF

chmod +x backup_version.sh
```

### Usage

```bash
# Create a backup
./backup_version.sh

# Result: ../ASP_DI_backups/ASP_DI_20260313_125923/
```

### Restore from Backup

```bash
# List backups
ls -lt ../ASP_DI_backups/

# Restore specific version
cp -r ../ASP_DI_backups/ASP_DI_20260313_125923/* .
```

---

## Option 3: Cloud Storage with Versions

### Using OneDrive/Google Drive

1. Move project to cloud folder:
```bash
mv /mnt/c/Users/EPOSYMU/python/kiro/ASP_DI /mnt/c/Users/EPOSYMU/OneDrive/ASP_DI
cd /mnt/c/Users/EPOSYMU/OneDrive/ASP_DI
```

2. Enable version history in OneDrive/Google Drive settings

3. Access previous versions through cloud interface

---

## Option 4: Compressed Archives

### Create Versioned Archives

```bash
# Create archive with version number
VERSION="v1.2"
tar -czf "ASP_DI_${VERSION}_$(date +%Y%m%d).tar.gz" \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='.pytensor' \
    .

# Result: ASP_DI_v1.2_20260313.tar.gz
```

### Extract Archive

```bash
# Extract to new directory
mkdir ASP_DI_v1.2
tar -xzf ASP_DI_v1.2_20260313.tar.gz -C ASP_DI_v1.2
```

---

## Recommended Workflow

### Daily Work

```bash
# Start of day: ensure you're on latest
git pull  # if using remote repo

# Make changes to code
# ... edit files ...

# End of day: commit changes
git add .
git commit -m "Added feature X, fixed bug Y"
```

### Before Major Changes

```bash
# Create a branch for experimentation
git checkout -b experiment-new-feature

# Make changes
# ... edit files ...

# If successful, merge back
git checkout main
git merge experiment-new-feature

# If unsuccessful, discard
git checkout main
git branch -D experiment-new-feature
```

### Before Presentations

```bash
# Tag the version you'll demo
git tag -a demo-2026-03-13 -m "Version for team presentation"

# Create backup
./backup_version.sh

# If demo goes wrong, you can restore
git checkout demo-2026-03-13
```

---

## Version Naming Convention

### Semantic Versioning

Format: `vMAJOR.MINOR.PATCH`

- **MAJOR**: Breaking changes (v1.0 → v2.0)
- **MINOR**: New features (v1.0 → v1.1)
- **PATCH**: Bug fixes (v1.1.0 → v1.1.1)

### Examples

- `v1.0.0` - Initial Bayesian Analytics
- `v1.1.0` - Added continuous learning simulator
- `v1.1.1` - Fixed data volume bug
- `v1.2.0` - Added posterior distributions
- `v2.0.0` - Added Module 2 (breaking change)

---

## What to Track

### Always Track:
- ✅ Python code (*.py)
- ✅ Documentation (*.md)
- ✅ Requirements (requirements.txt)
- ✅ Configuration files

### Optional:
- ⚠️ Generated data (data/*.csv) - can be regenerated
- ⚠️ Visualizations (*.png) - can be regenerated

### Never Track:
- ❌ Virtual environment (venv/)
- ❌ Cache files (__pycache__/)
- ❌ PyTensor cache (.pytensor/)
- ❌ IDE settings (.vscode/, .idea/)

---

## Quick Reference Commands

```bash
# Git version control
git init                          # Initialize repo
git add .                         # Stage all changes
git commit -m "message"           # Commit changes
git tag -a v1.0 -m "message"      # Tag version
git log --oneline                 # View history
git checkout v1.0                 # View old version
git checkout main                 # Return to latest

# Manual backup
./backup_version.sh               # Create backup
ls -lt ../ASP_DI_backups/         # List backups
cp -r ../ASP_DI_backups/XXX/* .   # Restore backup

# Archive
tar -czf ASP_DI_v1.0.tar.gz .     # Create archive
tar -xzf ASP_DI_v1.0.tar.gz       # Extract archive
```

---

## Remote Backup (GitHub/GitLab)

### Setup GitHub Repository

```bash
# Create repo on github.com, then:
git remote add origin https://github.com/yourusername/ASP_DI.git
git branch -M main
git push -u origin main
git push --tags
```

### Daily Sync

```bash
# Push changes to remote
git push

# Pull changes from remote
git pull
```

### Benefits:
- ✅ Cloud backup
- ✅ Access from anywhere
- ✅ Collaboration ready
- ✅ Full version history
- ✅ Issue tracking

---

## Recovery Scenarios

### "I broke something, need yesterday's version"
```bash
git log --oneline
git checkout <commit-hash>
# or
cp -r ../ASP_DI_backups/ASP_DI_20260312_* .
```

### "I want to compare current vs last week"
```bash
git diff HEAD~7 HEAD
```

### "I need the version I demoed last month"
```bash
git checkout demo-2026-02-13
```

### "I accidentally deleted files"
```bash
git checkout -- .
# or
git reset --hard HEAD
```

---

## Best Practices

1. **Commit often**: Small, focused commits are better than large ones
2. **Write clear messages**: "Fixed bug" → "Fixed data volume mismatch in ASP_C"
3. **Tag milestones**: Before demos, presentations, or major changes
4. **Backup before experiments**: Create branch or backup before risky changes
5. **Test before committing**: Ensure code runs before committing
6. **Document changes**: Update CHANGELOG.md with each version

---

## Current Status

Your project should now have:
- ✅ Fixed data volume bug (ASP_A: 30, ASP_B: 15, ASP_C: 5)
- ✅ All enhancement features working
- ✅ Complete documentation

**Next step**: Initialize git and create v1.2.0 tag!

```bash
cd /mnt/c/Users/EPOSYMU/python/kiro/ASP_DI
git init
git add .
git commit -m "Version 1.2.0: Complete Bayesian Analytics with continuous learning"
git tag -a v1.2.0 -m "Version 1.2.0: Production-ready Bayesian Analytics"
```
