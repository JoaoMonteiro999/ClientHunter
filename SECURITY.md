# Security Setup for ClientHunter

## ⚠️ IMPORTANT SECURITY NOTICE

This application requires email credentials to function. **NEVER** commit sensitive information to git!

## Setup Instructions

### Option 1: Using config.py (Recommended for development)

1. Copy the template:
   ```bash
   cp config_template.py config.py
   ```

2. Edit `config.py` with your actual email credentials:
   ```python
   EMAIL_REMETENTE = "your-email@gmail.com"
   SENHA_APP = "your-gmail-app-password"
   ```

3. The `config.py` file is already ignored by git and will not be committed.

### Option 2: Using Environment Variables (Recommended for production)

Set these environment variables:
```bash
export EMAIL_REMETENTE="your-email@gmail.com"
export SENHA_APP="your-gmail-app-password"
export SMTP_SERVER="smtp.gmail.com"
export SMTP_PORT="587"
```

## Getting Gmail App Password

1. Go to your Google Account settings
2. Enable 2-Factor Authentication
3. Go to "App passwords" 
4. Generate a new app password for "Mail"
5. Use this 16-character password (not your regular Gmail password)

## Files That Are Excluded from Git

- `config.py` - Contains email credentials
- `sent_emails_log.json` - Contains email history
- `results/` - Contains scraped email lists
- Any `*.csv` files with email data

## Before Committing

Always verify that no sensitive data is being committed:
```bash
git status
git diff --cached
```
