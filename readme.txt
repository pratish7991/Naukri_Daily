
Naukri Daily Resume Upload Automation

Project purpose
This project automates uploading your resume on Naukri using Selenium and Chrome/Chromium in headless mode.
It also reads the OTP from your Gmail inbox, submits the OTP automatically, uploads the resume file, and sends a success notification email.

Files in this project
- NaukriUpdateDaily.py
  Main automation script.
- .github/workflows/naukri-daily.yml
  GitHub Actions workflow for running the job in the cloud.
- requirements.txt
  Python dependencies.
- readme.txt
  Setup and usage documentation.
- PratishDewanganMLE.pdf
  Default resume file used by the script.

How the script works
1. Load environment variables from .env or GitHub repository secrets.
2. Open Naukri login page.
3. Log in using NAUKRI_EMAIL and NAUKRI_PASSWORD.
4. Detect OTP verification page.
5. Read the latest OTP from Gmail using IMAP.
6. Submit the OTP automatically.
7. Open the profile page.
8. Upload the resume file.
9. Send a notification email after success.

Important note
The script depends on a real Chrome/Chromium browser and a working Gmail app password for OTP retrieval.
If Google blocks the login flow or the OTP email structure changes, the automation may need manual validation.

Required local setup
1. Install Python 3.11+
2. Create and activate a virtual environment
3. Install dependencies

Example:
- macOS/Linux:
  python3 -m venv .venv
  source .venv/bin/activate
  pip install -r requirements.txt

- Windows:
  py -3.11 -m venv .venv
  .venv\Scripts\activate
  pip install -r requirements.txt

Environment variables to set
Create a .env file in the project root with these keys:

NAUKRI_EMAIL=your_naukri_email
NAUKRI_PASSWORD=your_naukri_password
SENDER_EMAIL=your_email_sender
SENDER_APP_PASSWORD=your_gmail_app_password
RECEIVER_EMAIL=your_notification_receiver
EMAIL_ADDRESS=your_email_address_for_otp_read
EMAIL_APP_PASSWORD=your_gmail_app_password_for_otp_read
HEADLESS=1
RESUME_PATH=/absolute/path/to/your/resume.pdf

Notes:
- If RESUME_PATH is omitted, the script will use the default file in the project folder.
- HEADLESS=1 is recommended for GitHub Actions and headless automation.
- Do not commit your real .env file to GitHub.

Gmail app password setup
Because Gmail does not allow regular account passwords for app automation, generate an app password.

Steps:
1. Open https://myaccount.google.com/apppasswords
2. Choose App = Mail
3. Choose Device = Windows Computer
4. Copy the 16-character password
5. Use that password in SENDER_APP_PASSWORD and EMAIL_APP_PASSWORD

Required GitHub secrets for Actions
In the GitHub repository, add these repository secrets:

NAUKRI_EMAIL
NAUKRI_PASSWORD
SENDER_EMAIL
SENDER_APP_PASSWORD
RECEIVER_EMAIL
EMAIL_ADDRESS
EMAIL_APP_PASSWORD
HEADLESS

The GitHub workflow file is:
.github/workflows/naukri-daily.yml

This workflow uses workflow_dispatch, which means it is designed to be started manually or by an external scheduler.

How to run locally
From the project folder:

python NaukriUpdateDaily.py

Or if using the virtual environment:

source .venv/bin/activate
python NaukriUpdateDaily.py

Expected behavior:
- Selenium opens Chrome/Chromium
- Naukri login page is accessed
- OTP is read from Gmail inbox
- Resume is uploaded
- Success email is sent if everything works

How the GitHub Actions workflow works
The workflow file triggers on workflow_dispatch only.
That means GitHub itself is not used as the scheduler.
Instead, another scheduler should trigger the workflow by calling the GitHub Actions dispatch API.

Recommended free external scheduler
Use cron-job.org or any similar free external cron service.

GitHub workflow dispatch endpoint for this repo
Owner: pratish7991
Repository: Naukri_Daily
Workflow file: naukri-daily.yml
Branch: main

Dispatch URL:
https://api.github.com/repos/pratish7991/Naukri_Daily/actions/workflows/naukri-daily.yml/dispatches

Example curl request:
curl -X POST \
  -H "Accept: application/vnd.github+json" \
  -H "Authorization: Bearer YOUR_GITHUB_PERSONAL_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  https://api.github.com/repos/pratish7991/Naukri_Daily/actions/workflows/naukri-daily.yml/dispatches \
  -d '{"ref":"main"}'

GitHub token setup
Create a GitHub Personal Access Token (PAT) from:
GitHub -> Settings -> Developer settings -> Personal access tokens

Recommended token permission:
- repo for private repositories
- public_repo for public repositories
- workflow permission if your account requires it

Important:
- Do not expose the personal access token in public repositories or screenshots.
- This token is used only to trigger the GitHub Action from your external scheduler.

How to confirm the setup is complete
Use this checklist:

1. Local run succeeds
   - python NaukriUpdateDaily.py
   - The script reaches the profile page and uploads the resume file.

2. .env file is configured correctly
   - All required keys are present.
   - Gmail app passwords are valid.

3. GitHub secrets are added
   - All workflow env secrets exist in the repository.

4. GitHub Actions workflow dispatch works
   - Run the curl command above.
   - Expected response: HTTP 204 No Content.
   - Then check the Actions tab in GitHub for a new workflow run.

5. External scheduler is configured
   - cron-job.org or another scheduler is calling the GitHub workflow dispatch URL.
   - The schedule is set to your desired time.

6. Email notifications are functioning
   - Success email is sent to RECEIVER_EMAIL after upload.
   - OTP email is read from EMAIL_ADDRESS mailbox.

Common troubleshooting
1. 403 Forbidden on workflow dispatch
   - PAT is missing permission
   - PAT is invalid or expired
   - Token lacks Actions access for the repository
   - Branch name is wrong

2. Resume upload fails
   - Resume file path is wrong
   - Chrome/Chromium binary not found
   - File not accessible

3. OTP not detected
   - Gmail app password is wrong
   - IMAP access is blocked or not enabled
   - OTP email is not in inbox or not unread

4. GitHub Actions run fails
   - Required GitHub secrets are missing
   - Chromium install step fails
   - The script cannot find the browser binary or resume file

5. Browser or Selenium issue
   - ChromeDriver version mismatch
   - Old installed environment or dependency mismatch

Recommended verification flow
After setup, run the steps in this order:
1. Verify local .env setup
2. Run the script locally once
3. Verify GitHub secrets are added
4. Trigger the workflow manually from GitHub Actions UI
5. Trigger the same workflow using curl
6. Set the external scheduler time
7. Confirm the GitHub Actions log shows a successful run

Final note
This project is reliable only when all secrets, app passwords, and credentials are correct.
GitHub's built-in cron schedule is not guaranteed to run exactly on time, so an external scheduler is the recommended way to keep the automation dependable.
