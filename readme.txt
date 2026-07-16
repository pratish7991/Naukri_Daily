
# Naukri Daily Resume Upload Automation

## Overview
This project automates uploading your resume on Naukri using Selenium and Chrome/Chromium in headless mode.
It also reads the OTP from your Gmail inbox, submits the OTP automatically, uploads the resume file, and sends a success notification email.

## Project Structure
- `NaukriUpdateDaily.py` — Main automation script
- `.github/workflows/naukri-daily.yml` — GitHub Actions workflow for cloud execution
- `requirements.txt` — Python dependencies
- `readme.txt` — Setup and usage documentation
- `PratishDewanganMLE.pdf` — Default resume file used by the script

## How the Script Works
1. Load environment variables from `.env` or GitHub repository secrets.
2. Open the Naukri login page.
3. Log in using `NAUKRI_EMAIL` and `NAUKRI_PASSWORD`.
4. Detect the OTP verification page.
5. Read the latest OTP from Gmail using IMAP.
6. Submit the OTP automatically.
7. Open the profile page.
8. Upload the resume file.
9. Send a notification email after success.

> Note: The script depends on a real Chrome/Chromium browser and a working Gmail app password for OTP retrieval.

## Local Setup

### 1. Install Python
Use Python 3.11 or newer.

### 2. Create a virtual environment

#### macOS/Linux
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

#### Windows
```powershell
py -3.11 -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Variables
Create a `.env` file in the project root with the following keys:

```env
NAUKRI_EMAIL=your_naukri_email
NAUKRI_PASSWORD=your_naukri_password
SENDER_EMAIL=your_email_sender
SENDER_APP_PASSWORD=your_gmail_app_password
RECEIVER_EMAIL=your_notification_receiver
EMAIL_ADDRESS=your_email_address_for_otp_read
EMAIL_APP_PASSWORD=your_gmail_app_password_for_otp_read
HEADLESS=1
RESUME_PATH=/absolute/path/to/your/resume.pdf
```

### Notes
- If `RESUME_PATH` is omitted, the script uses the default PDF file in the project folder.
- `HEADLESS=1` is recommended for GitHub Actions and automation.
- Do not commit your real `.env` file to GitHub.

## Gmail App Password Setup
Because Gmail does not allow regular account passwords for automation, generate an app password.

### Steps
1. Open https://myaccount.google.com/apppasswords
2. Choose `App = Mail`
3. Choose `Device = Windows Computer`
4. Copy the 16-character password
5. Use that password in `SENDER_APP_PASSWORD` and `EMAIL_APP_PASSWORD`

## GitHub Secrets for Actions
Add these repository secrets in GitHub:

- `NAUKRI_EMAIL`
- `NAUKRI_PASSWORD`
- `SENDER_EMAIL`
- `SENDER_APP_PASSWORD`
- `RECEIVER_EMAIL`
- `EMAIL_ADDRESS`
- `EMAIL_APP_PASSWORD`
- `HEADLESS`

Workflow file:
- `.github/workflows/naukri-daily.yml`

This workflow uses `workflow_dispatch`, which means it is designed to be started manually or by an external scheduler.

## Run Locally
From the project folder:

```bash
python NaukriUpdateDaily.py
```

Or with the virtual environment activated:

```bash
source .venv/bin/activate
python NaukriUpdateDaily.py
```

## Expected Behavior
- Selenium opens Chrome/Chromium
- The Naukri login page is accessed
- The OTP is read from the Gmail inbox
- The resume is uploaded
- A success email is sent if everything works correctly

## GitHub Actions Workflow
The workflow file triggers only on `workflow_dispatch`.
That means GitHub itself is not used as the scheduler.
Instead, another scheduler should trigger the workflow by calling the GitHub Actions dispatch API.

## Recommended Free External Scheduler
Use `cron-job.org` or any similar free external cron service.

## GitHub Workflow Dispatch Endpoint
For this repository:
- Owner: `pratish7991`
- Repository: `Naukri_Daily`
- Workflow file: `naukri-daily.yml`
- Branch: `main`

### Dispatch URL
```text
https://api.github.com/repos/pratish7991/Naukri_Daily/actions/workflows/naukri-daily.yml/dispatches
```

### Example `curl` Request
```bash
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_GITHUB_PERSONAL_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/pratish7991/Naukri_Daily/actions/workflows/naukri-daily.yml/dispatches \
  -d '{"ref":"main"}'
```

## GitHub Token Setup
Create a GitHub Personal Access Token (PAT) from:
- GitHub → Settings → Developer settings → Personal access tokens

### Recommended Token Permissions
- `repo` for private repositories
- `public_repo` for public repositories
- `workflow` permission if your account requires it

> Important: Do not expose the personal access token in public repositories or screenshots.

## How to Confirm the Setup Is Complete
Use this checklist:

1. Local run succeeds
   - `python NaukriUpdateDaily.py`
   - The script reaches the profile page and uploads the resume file.

2. `.env` file is configured correctly
   - All required keys are present.
   - Gmail app passwords are valid.

3. GitHub secrets are added
   - All workflow env secrets are present in the repository.

4. GitHub Actions workflow dispatch works
   - Run the `curl` command above.
   - Expected response: `HTTP 204 No Content`.
   - Then check the Actions tab in GitHub for a new workflow run.

5. External scheduler is configured
   - `cron-job.org` or another scheduler is calling the GitHub workflow dispatch URL.
   - The schedule is set to your desired time.

6. Email notifications are functioning
   - A success email is sent to `RECEIVER_EMAIL` after upload.
   - The OTP email is read from the `EMAIL_ADDRESS` mailbox.

## Common Troubleshooting

### 1. `403 Forbidden` on workflow dispatch
- PAT is missing permission
- PAT is invalid or expired
- Token lacks Actions access for the repository
- Branch name is wrong

### 2. Resume upload fails
- Resume file path is wrong
- Chrome/Chromium binary is not found
- File is not accessible

### 3. OTP not detected
- Gmail app password is wrong
- IMAP access is blocked or not enabled
- OTP email is not in the inbox or not unread

### 4. GitHub Actions run fails
- Required GitHub secrets are missing
- Chromium install step fails
- The script cannot find the browser binary or resume file

### 5. Browser or Selenium issue
- ChromeDriver version mismatch
- Dependency mismatch in the environment

## Recommended Verification Flow
After setup, run the steps in this order:
1. Verify the local `.env` setup
2. Run the script locally once
3. Verify GitHub secrets are added
4. Trigger the workflow manually from the GitHub Actions UI
5. Trigger the same workflow using `curl`
6. Set the external scheduler time
7. Confirm the GitHub Actions log shows a successful run

## Final Note
This project is reliable only when all secrets, app passwords, and credentials are correct.
GitHub's built-in cron schedule is not guaranteed to run exactly on time, so an external scheduler is the recommended way to keep the automation dependable.
