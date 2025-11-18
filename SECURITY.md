# Security Guidelines

This document outlines security best practices for the Shrimp Vision project.

## 🔒 Protected Information

The following types of sensitive information are automatically excluded from git via `.gitignore`:

### Environment Variables
- `.env` files (all variants)
- `.env.local`, `.env.development.local`, `.env.production.local`
- Any file matching `*.env` pattern

### Secrets and Keys
- `*.secret` files
- `*.key` files
- Certificate files: `*.pem`, `*.p12`, `*.pfx`, `*.jks`, `*.keystore`, `*.crt`, `*.cer`, `*.csr`
- `secrets/` directory
- `secrets.yaml` and `secrets.yml` files
- `config/secrets.*` files

### User Data
- Uploaded images (`backend/static/uploads/*`)
- Annotations (`backend/static/annotations/*`)
- Trained models (`backend/models/*`)
- Datasets (`backend/dataset/*`)
- Exports (`backend/exports/*`)

### Logs and Cache
- All log files (`*.log`)
- Cache files (`*.cache`)
- Database files (`*.db`, `*.sqlite`, `*.sqlite3`)

## ✅ Security Checklist

Before committing code, ensure:

- [ ] No API keys or secrets are hardcoded in source files
- [ ] All sensitive configuration uses environment variables
- [ ] `.env` files are never committed
- [ ] No credentials are in comments or documentation
- [ ] User-uploaded data is excluded from git
- [ ] Log files don't contain sensitive information

## 🛡️ Best Practices

1. **Use Environment Variables**: Store all secrets in `.env` files (which are gitignored)
2. **Never Commit Secrets**: Even if they're in `.gitignore`, double-check before committing
3. **Use `.env.example`**: Create example files with placeholder values for documentation
4. **Review Diffs**: Always review `git diff` before committing
5. **Rotate Secrets**: If secrets are accidentally committed, rotate them immediately

## 🚨 If Secrets Are Accidentally Committed

If sensitive information is accidentally committed:

1. **Immediately rotate the exposed secrets**
2. **Remove from git history**:
   ```bash
   git filter-branch --force --index-filter \
     "git rm --cached --ignore-unmatch path/to/secret-file" \
     --prune-empty --tag-name-filter cat -- --all
   ```
3. **Force push** (coordinate with team first):
   ```bash
   git push origin --force --all
   ```
4. **Notify team members** to re-clone the repository

## 📝 Environment Variable Template

Create a `.env.example` file (this CAN be committed) with:

```bash
# Backend Configuration
BACKEND_PORT=3100
ENVIRONMENT=development

# Frontend Configuration  
NEXT_PUBLIC_API_URL=http://localhost:3100

# Add other non-sensitive defaults here
```

Users can copy this to `.env.local` and fill in actual values.

## 🔍 Verification

To verify your `.gitignore` is working:

```bash
# Check if a file is ignored
git check-ignore -v path/to/file

# List all tracked files (should not include .env files)
git ls-files | grep -E "\.env|secret|key"

# Check git status (should not show ignored files)
git status
```

