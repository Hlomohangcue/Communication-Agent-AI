# Git Repository Guide

## ✅ Repository Initialized

Your Git repository has been successfully created with:
- **Username**: hlomohangcue
- **Email**: hlomohangsethuntsa3@gmail.com
- **Branch**: master
- **Initial Commit**: 717848b

## 📦 What's Included

33 files committed:
- Backend Python code (agents, coordinator, database, simulation)
- Frontend HTML/CSS/JavaScript
- Documentation (README, deployment guides, checklists)
- Configuration files (Dockerfile, requirements.txt, .gitignore)
- Speech recognition fixes and test pages

## 🚫 What's Excluded (.gitignore)

These files are automatically ignored:
- `__pycache__/` - Python cache files
- `*.pyc`, `*.pyo`, `*.pyd` - Compiled Python
- `*.db` - Database files (including communication_bridge.db)
- `.env` - Your API keys (IMPORTANT: never commit this!)
- `venv/`, `env/` - Virtual environments
- `*.log` - Log files

## 🔑 Common Git Commands

### Check Status
```bash
git status
```
Shows modified, staged, and untracked files.

### Add Files
```bash
# Add specific file
git add filename.py

# Add all changes
git add .

# Add all Python files
git add *.py
```

### Commit Changes
```bash
# Commit with message
git commit -m "Your commit message here"

# Commit all tracked changes
git commit -am "Your message"
```

### View History
```bash
# Show commit history
git log

# Show compact history
git log --oneline

# Show last 5 commits
git log -5

# Show changes in commits
git log -p
```

### View Changes
```bash
# Show unstaged changes
git diff

# Show staged changes
git diff --cached

# Show changes in specific file
git diff filename.py
```

### Branches
```bash
# List branches
git branch

# Create new branch
git branch feature-name

# Switch to branch
git checkout feature-name

# Create and switch to new branch
git checkout -b feature-name

# Merge branch into current
git merge feature-name

# Delete branch
git branch -d feature-name
```

### Undo Changes
```bash
# Discard changes in file
git checkout -- filename.py

# Unstage file
git reset HEAD filename.py

# Undo last commit (keep changes)
git reset --soft HEAD~1

# Undo last commit (discard changes)
git reset --hard HEAD~1
```

## 🌐 Push to GitHub

### 1. Create GitHub Repository
1. Go to https://github.com/new
2. Repository name: `communication-bridge-ai`
3. Don't initialize with README (you already have one)
4. Click "Create repository"

### 2. Add Remote and Push
```bash
# Add GitHub as remote
git remote add origin https://github.com/hlomohangcue/communication-bridge-ai.git

# Push to GitHub
git push -u origin master
```

### 3. For Subsequent Pushes
```bash
git push
```

## 📝 Recommended Workflow

### Daily Work
```bash
# 1. Check what changed
git status

# 2. Add your changes
git add .

# 3. Commit with descriptive message
git commit -m "Add feature: description of what you did"

# 4. Push to GitHub (if set up)
git push
```

### Good Commit Messages
```bash
# ✅ Good
git commit -m "Fix speech recognition continuous recording issue"
git commit -m "Add microphone test page for troubleshooting"
git commit -m "Update README with deployment instructions"

# ❌ Bad
git commit -m "fix"
git commit -m "changes"
git commit -m "update"
```

## 🔒 Security Reminders

### NEVER Commit These:
- `.env` file (contains API keys)
- Database files with real data
- Passwords or secrets
- Personal information

### If You Accidentally Commit Secrets:
```bash
# Remove file from Git but keep locally
git rm --cached .env

# Commit the removal
git commit -m "Remove .env from repository"

# IMPORTANT: Change your API keys immediately!
# The old keys are still in Git history
```

## 🏷️ Tagging Releases

```bash
# Create a tag
git tag -a v1.0.0 -m "Initial release"

# Push tags to GitHub
git push --tags

# List tags
git tag
```

## 🔄 Keeping Track of Changes

### Before Making Changes
```bash
# Create a feature branch
git checkout -b feature/new-agent

# Make your changes...

# Commit changes
git commit -am "Add new agent functionality"

# Switch back to master
git checkout master

# Merge feature
git merge feature/new-agent
```

## 📊 View Project Stats

```bash
# Count commits
git rev-list --count HEAD

# Show contributors
git shortlog -sn

# Show file changes
git diff --stat

# Show lines added/removed
git log --stat
```

## 🆘 Troubleshooting

### "fatal: not a git repository"
```bash
# Make sure you're in the project directory
cd "C:\Users\OnePower\OneDrive\Desktop\Communication Agent AI"
```

### Merge Conflicts
```bash
# 1. Open conflicted files
# 2. Look for <<<<<<< HEAD markers
# 3. Edit to resolve conflicts
# 4. Remove conflict markers
# 5. Add resolved files
git add resolved-file.py
# 6. Commit
git commit -m "Resolve merge conflict"
```

### Accidentally Committed Wrong Files
```bash
# Undo last commit, keep changes
git reset --soft HEAD~1

# Remove unwanted files
git reset HEAD unwanted-file.py

# Commit again
git commit -m "Correct commit"
```

## 📚 Next Steps

1. **Push to GitHub**: Follow the "Push to GitHub" section above
2. **Create .gitignore for IDE**: Add your IDE-specific files
3. **Set up branches**: Create `development` branch for testing
4. **Add collaborators**: Invite team members on GitHub
5. **Enable GitHub Actions**: Set up CI/CD for automated testing

## 🎯 Current Repository Status

```
Repository: communication-bridge-ai (local)
Branch: master
Commits: 1
Files: 33
User: hlomohangcue <hlomohangsethuntsa3@gmail.com>
```

## 💡 Tips

1. **Commit Often**: Small, frequent commits are better than large ones
2. **Write Clear Messages**: Future you will thank present you
3. **Use Branches**: Keep master stable, experiment in branches
4. **Pull Before Push**: If working with others, always pull first
5. **Review Before Commit**: Use `git diff` to check your changes

## 🔗 Useful Resources

- Git Documentation: https://git-scm.com/doc
- GitHub Guides: https://guides.github.com/
- Git Cheat Sheet: https://education.github.com/git-cheat-sheet-education.pdf
- Interactive Git Tutorial: https://learngitbranching.js.org/
