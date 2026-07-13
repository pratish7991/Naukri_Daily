Generate an App Password if you're using Gmail (you can’t use your regular Gmail password due to security).

🔐 Step 1: Set Up Gmail App Password (once)
Go to: https://myaccount.google.com/apppasswords

Choose:
- App: Mail
- Device: Other (Custom name) or your current device

Copy the 16-digit password and save it safely.

✅ Step 2: Configure environment variables
Create a `.env` file locally (do not commit it) or use GitHub Actions secrets.

Example `.env`:
```
NAUKRI_EMAIL=your_naukri_email@example.com
NAUKRI_PASSWORD=your_naukri_password
SENDER_EMAIL=your_email@gmail.com
SENDER_APP_PASSWORD=your_app_password
RECEIVER_EMAIL=your_email@gmail.com
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_APP_PASSWORD=your_app_password
RESUME_PATH=PratishDewanganMLE.pdf
HEADLESS=1
```

> Note: `RESUME_PATH` should point to your resume file. The default path is the repository root file `PratishDewanganMLE.pdf`.

✅ Step 3: Install dependencies
Run:
```
pip install -r requirements.txt
```

✅ Step 4: Run locally to verify
Run:
```
python NaukriUpdateDaily.py
```

If it logs in and uploads your resume, the script is working.

---

## Daily automation with GitHub Actions
This repository already includes a GitHub Actions workflow at `.github/workflows/naukri-daily.yml`.

### Add GitHub Secrets
In your repository on GitHub, go to:
`Settings` → `Secrets and variables` → `Actions`

Add these secrets:
- `NAUKRI_EMAIL`
- `NAUKRI_PASSWORD`
- `SENDER_EMAIL`
- `SENDER_APP_PASSWORD`
- `RECEIVER_EMAIL`
- `EMAIL_ADDRESS`
- `EMAIL_APP_PASSWORD`

### Schedule
The workflow is configured to run daily at 07:00 IST.

### Manual trigger
You can also run it manually from GitHub:
1. Open `Actions`
2. Select `Naukri Daily Resume Upload`
3. Click `Run workflow`

---

## How it works
1. The script logs into Naukri with your credentials.
2. It detects OTP verification and tries to fetch the OTP from Gmail.
3. It uploads your resume file.
4. It sends a success email to the receiver address.

---

## Important notes
- Do not commit `.env` to the repository.
- Use GitHub secrets for any credentials used in the workflow.
- If Naukri changes the login flow, you may need to update the script.
- Keep your resume file name and path correct.

---

## Local vs Cloud
- Local: use `.env` and run `python NaukriUpdateDaily.py`
- Cloud: use GitHub Actions and repo secrets for fully automated daily runs

