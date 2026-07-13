from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import time
import os
import sys
import imaplib
import email
import re
import traceback
from pathlib import Path

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==== 🔐 Environment Configuration ====
load_dotenv()
NAUKRI_EMAIL = os.environ.get('NAUKRI_EMAIL')
NAUKRI_PASSWORD = os.environ.get('NAUKRI_PASSWORD')
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_APP_PASSWORD = os.environ.get('SENDER_APP_PASSWORD')
RECEIVER_EMAIL = os.environ.get('RECEIVER_EMAIL')
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS', SENDER_EMAIL)
EMAIL_APP_PASSWORD = os.environ.get('EMAIL_APP_PASSWORD', SENDER_APP_PASSWORD)
RESUME_PATH = Path(os.environ.get('RESUME_PATH')).expanduser() if os.environ.get('RESUME_PATH') else Path.cwd() / 'PratishDewanganMLE.pdf'
RESUME_PATH = RESUME_PATH.resolve()
HEADLESS = os.environ.get('HEADLESS', '1') == '1'


def get_chrome_binary():
    if sys.platform.startswith('darwin'):
        return '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

    candidates = [
        '/usr/bin/google-chrome-stable',
        '/usr/bin/google-chrome',
        '/usr/bin/chromium-browser',
        '/usr/bin/chromium',
    ]
    for candidate in candidates:
        if Path(candidate).exists():
            return candidate
    return None


def find_otp_inputs(driver):
    xpath = "//input[(contains(translate(@name,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'OTP') or contains(translate(@id,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'OTP') or contains(translate(@placeholder,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'OTP') or contains(translate(@aria-label,'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'OTP')) and not(@type='hidden')]"
    inputs = driver.find_elements(By.XPATH, xpath)
    if inputs:
        return [inp for inp in inputs if inp.is_displayed()]

    fallback = driver.find_elements(By.XPATH, "//input[(self::input[@type='tel'] or self::input[@type='number'] or self::input[@type='text']) and not(@type='hidden')]")
    visible = [inp for inp in fallback if inp.is_displayed()]
    if visible:
        return visible[:6]

    # fallback to any visible input fields if nothing else matches
    return [inp for inp in driver.find_elements(By.XPATH, "//input[not(@type='hidden')]") if inp.is_displayed()][:6]


def fetch_naukri_otp():
    if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
        raise RuntimeError('Email credentials not configured for OTP retrieval.')

    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    mail.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
    mail.select('inbox')

    search_terms = ['Naukri', 'naukri', 'OTP', 'One Time Password', 'Verification']
    message_ids = []
    for term in search_terms:
        status, data = mail.search(None, f'(UNSEEN SUBJECT "{term}")')
        if status == 'OK' and data and data[0]:
            message_ids = data[0].split()
            break

    if not message_ids:
        status, data = mail.search(None, '(UNSEEN)')
        if status == 'OK' and data and data[0]:
            message_ids = data[0].split()

    if not message_ids:
        raise RuntimeError('No unread email found for OTP retrieval.')

    latest_id = message_ids[-1]
    status, data = mail.fetch(latest_id, '(RFC822)')
    if status != 'OK':
        raise RuntimeError('Failed to fetch OTP email.')

    raw_email = data[0][1]
    message = email.message_from_bytes(raw_email)

    body = ''
    if message.is_multipart():
        for part in message.walk():
            if part.get_content_type() == 'text/plain' and part.get_content_disposition() != 'attachment':
                body = part.get_payload(decode=True).decode(errors='ignore')
                break
    else:
        body = message.get_payload(decode=True).decode(errors='ignore')

    match = re.search(r'\b(\d{4,8})\b', body)
    if not match:
        raise RuntimeError('Could not find OTP code in email body.')

    return match.group(1)

# ==== 🚀 Main Function ====
def upload_resume():
    if not NAUKRI_EMAIL or not NAUKRI_PASSWORD:
        raise RuntimeError('Missing NAUKRI_EMAIL or NAUKRI_PASSWORD environment variable.')
    if not SENDER_EMAIL or not SENDER_APP_PASSWORD or not RECEIVER_EMAIL:
        raise RuntimeError('Missing email settings in environment variables.')
    if not RESUME_PATH.exists():
        raise FileNotFoundError(f'Resume file not found at: {RESUME_PATH}')

    print(f"Using resume path: {RESUME_PATH}")
    print(f"HEADLESS mode: {HEADLESS}")

    # Set up Chrome driver
    options = webdriver.ChromeOptions()
    if HEADLESS:
        options.add_argument("--headless=new")
    options.add_argument("--remote-allow-origins=*")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-extensions")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_argument("--disable-infobars")
    options.add_argument("--start-maximized")
    options.add_argument("--window-size=1920,1080")
    options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Safari/537.36")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    chrome_binary = get_chrome_binary()
    if chrome_binary:
        options.binary_location = chrome_binary
        print(f"Using Chrome binary: {chrome_binary}")
    else:
        print("Warning: Chrome binary not found, relying on driver defaults.")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": "Object.defineProperty(navigator, 'webdriver', { get: () => undefined })"
    })

    wait = WebDriverWait(driver, 20)

    try:
        # Step 1: Open Naukri homepage
        driver.get("https://www.naukri.com/")
        time.sleep(2)

        # Step 2: Click on Login
        login_button = wait.until(EC.element_to_be_clickable((By.ID, "login_Layer")))
        login_button.click()
        time.sleep(1)

        # Step 3: Enter login details
        email_input = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//input[@placeholder='Enter your active Email ID / Username']")))
        email_input.clear()
        email_input.send_keys(NAUKRI_EMAIL)

        password_input = wait.until(EC.visibility_of_element_located(
            (By.XPATH, "//input[@placeholder='Enter your password']")))
        password_input.clear()
        password_input.send_keys(NAUKRI_PASSWORD)

        # Step 4: Click Login
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        print("✅ Login form submitted.")
        time.sleep(5)

        otp_inputs = find_otp_inputs(driver)
        if otp_inputs:
            print(f'🔐 Detected {len(otp_inputs)} OTP input(s). Retrieving email OTP...')
            otp_code = fetch_naukri_otp()
            print(f'🔐 Using OTP: {otp_code}')

            if len(otp_inputs) == 1:
                otp_inputs[0].clear()
                otp_inputs[0].send_keys(otp_code)
            else:
                for i, char in enumerate(otp_code):
                    if i < len(otp_inputs):
                        otp_inputs[i].clear()
                        otp_inputs[i].send_keys(char)

            try:
                submit_button = driver.find_element(By.XPATH, "//button[@type='submit' or contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'VERIFY') or contains(translate(text(),'abcdefghijklmnopqrstuvwxyz','ABCDEFGHIJKLMNOPQRSTUVWXYZ'),'SUBMIT')]")
                submit_button.click()
            except Exception:
                pass
            time.sleep(5)

        page_source = driver.page_source.lower()
        if any(term in page_source for term in [
            'otp', 'one-time password', 'one time password', 'two-step', 'two step',
            'verification code', 'verify your identity', 'send otp', 'enter otp'
        ]):
            raise RuntimeError('Naukri login requires OTP/verification. Automation cannot continue in this environment.')

        if 'mnjuser/profile' not in driver.current_url and 'login' in driver.current_url.lower():
            raise RuntimeError('Naukri login did not complete successfully. Check credentials or page behavior.')

        print("✅ Logged in successfully.")
        time.sleep(2)

        # Step 5: Go to profile page
        driver.get("https://www.naukri.com/mnjuser/profile")
        time.sleep(5)

        # Step 6: Upload resume
        upload_input = wait.until(EC.presence_of_element_located((By.XPATH, "//input[@type='file']")))
        upload_input.send_keys(str(RESUME_PATH))
        print("✅ Resume uploaded successfully!")

        time.sleep(5)
        send_success_email()


    except Exception as e:
        print("❌ Error occurred:", e)
        print(traceback.format_exc())
        try:
            driver.save_screenshot("error.png")
            with open('error_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
        except Exception:
            pass
    finally:
        driver.quit()


def send_success_email():
    subject = "✅ Naukri Resume Upload Success"
    body = "Hi Pratish,\n\nYour resume was successfully uploaded to Naukri.com.\n\nRegards,\nYour Automation Bot 🤖"

    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
        server.send_message(msg)
        server.quit()
        print("📧 Success email sent!")
    except Exception as e:
        print("❌ Failed to send email:", e)

# ==== 🔁 Run It ====
if __name__ == "__main__":
    try:
        upload_resume()
    except Exception as e:
        print("❌ Exited with error:", e)





