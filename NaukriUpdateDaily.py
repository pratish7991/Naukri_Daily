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
import html
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
OTP_LENGTH = 6
ARTIFACTS_DIR = Path.cwd() / 'artifacts'
DEBUG_FULL_EMAIL = os.environ.get('DEBUG_FULL_EMAIL', '1') == '1'


def get_chrome_binary():
    if sys.platform.startswith('darwin'):
        candidate = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'
        return candidate if Path(candidate).exists() else None

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

    # Do not treat arbitrary text fields as OTP fields. That can mistake the
    # login form or profile fields for an OTP challenge.
    return []


def clean_email_text(text):
    if not text:
        return ''
    text = re.sub(r'(?is)<(script|style).*?>.*?</\1>', ' ', text)
    text = re.sub(r'<[^>]+>', ' ', text)
    text = html.unescape(text)
    text = re.sub(r'[^0-9a-zA-Z\s\-]', ' ', text)
    text = re.sub(r'[\s\-]+', ' ', text)
    return text.strip()


def extract_otp_from_email_body(body, html_body, expected_length=OTP_LENGTH):
    text = clean_email_text(body)
    html_text = clean_email_text(html_body)
    full_text = ' '.join([part for part in [text, html_text] if part])

    if not full_text:
        return None

    otp_phrases = [
        r'otp',
        r'one time password',
        r'verification code',
        r'login code',
        r'security code',
        r'code to login',
        r'please enter below otp',
    ]

    for phrase in otp_phrases:
        for match in re.finditer(phrase, full_text, flags=re.IGNORECASE):
            tail = full_text[match.end():match.end() + 200]
            if expected_length:
                next_match = re.search(rf'(?<!\d)(\d{{{expected_length}}})(?!\d)', tail)
                if next_match:
                    return next_match.group(1)
            else:
                next_match = re.search(r'(?<!\d)(\d{6})(?!\d)', tail)
                if next_match:
                    return next_match.group(1)

    if expected_length:
        fallback_codes = re.findall(rf'(?<!\d)(\d{{{expected_length}}})(?!\d)', full_text)
        if fallback_codes:
            return fallback_codes[0]
    else:
        fallback_codes = re.findall(r'(?<!\d)(\d{6})(?!\d)', full_text)
        if fallback_codes:
            return fallback_codes[0]
        fallback_codes = re.findall(r'(?<!\d)(\d{5})(?!\d)', full_text)
        if fallback_codes:
            print('🔎 Fallback 5-digit matches found:', fallback_codes)
            return fallback_codes[0]
        fallback_codes = re.findall(r'(?<!\d)(\d{4})(?!\d)', full_text)
        if fallback_codes:
            print('🔎 Fallback 4-digit matches found:', fallback_codes)
            return fallback_codes[0]

    return None


def fetch_naukri_otp(expected_length=OTP_LENGTH):
    if not EMAIL_ADDRESS or not EMAIL_APP_PASSWORD:
        raise RuntimeError('Email credentials not configured for OTP retrieval.')

    print('📧 Starting OTP retrieval for:', EMAIL_ADDRESS)
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    try:
        mail.login(EMAIL_ADDRESS, EMAIL_APP_PASSWORD)
        mail.select('inbox')

        # Only accept unread messages that arrive for this login attempt. Using
        # older messages risks submitting an expired OTP.
        search_terms = ['Naukri', 'OTP', 'One Time Password', 'Verification']
        message_ids = []
        for attempt in range(12):
            print(f'⏳ Waiting for a new OTP email... attempt {attempt + 1}/12')
            for term in search_terms:
                status, data = mail.search(None, f'(UNSEEN SUBJECT "{term}")')
                if status == 'OK' and data and data[0]:
                    message_ids = data[0].split()
                    break
            if message_ids:
                break
            if attempt < 11:
                time.sleep(5)

        if not message_ids:
            raise RuntimeError('No new unread Naukri OTP email arrived within 60 seconds.')

        for message_id in reversed(message_ids[-10:]):
            status, data = mail.fetch(message_id, '(RFC822)')
            if status != 'OK' or not data or not data[0]:
                continue

            raw_email = data[0][1]
            if DEBUG_FULL_EMAIL:
                print('\n========== RAW OTP EMAIL START ==========')
                print(raw_email.decode('utf-8', errors='replace'))
                print('========== RAW OTP EMAIL END ============\n')

            message = email.message_from_bytes(raw_email)
            subject = message.get('Subject', '<no subject>')
            from_header = message.get('From', '<no sender>')
            date_header = message.get('Date', '<no date>')
            body = ''
            html_body = ''
            if message.is_multipart():
                for part in message.walk():
                    if part.get_content_maintype() == 'multipart' or part.get_content_disposition() == 'attachment':
                        continue
                    content_type = part.get_content_type()
                    payload = part.get_payload(decode=True)
                    if not payload:
                        continue
                    try:
                        decoded = payload.decode(part.get_content_charset() or 'utf-8', errors='ignore')
                    except Exception:
                        decoded = payload.decode(errors='ignore')
                    if content_type == 'text/plain':
                        body += decoded + '\n'
                    elif content_type == 'text/html':
                        html_body += decoded + '\n'
            else:
                content_type = message.get_content_type()
                payload = message.get_payload(decode=True)
                if payload:
                    try:
                        decoded = payload.decode(message.get_content_charset() or 'utf-8', errors='ignore')
                    except Exception:
                        decoded = payload.decode(errors='ignore')
                    if content_type == 'text/plain':
                        body = decoded
                    elif content_type == 'text/html':
                        html_body = decoded

            preview = (body or html_body or '').replace('\n', ' ').replace('\r', ' ').strip()
            if len(preview) > 400:
                preview = preview[:400] + '...'
            print(f'📩 Candidate email: subject="{subject}" from="{from_header}" date="{date_header}"')
            print('    preview:', preview)

            otp_code = extract_otp_from_email_body(body, html_body, expected_length)
            if otp_code:
                print(f'✅ Found OTP: {otp_code}')
                return otp_code

        raise RuntimeError('Could not find a 6-digit OTP in the new Naukri email.')
    finally:
        try:
            mail.logout()
        except Exception:
            pass


def wait_for_upload_confirmation(driver, timeout=30):
    confirmation_xpath = (
        "//*[contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'resume uploaded') "
        "or contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'resume has been uploaded') "
        "or contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'successfully uploaded')]"
    )
    WebDriverWait(driver, timeout).until(
        EC.visibility_of_element_located((By.XPATH, confirmation_xpath))
    )


def find_resume_upload_input(driver, timeout=30):
    """Locate Naukri's file input across its profile and resume-upload pages."""
    file_input_locator = (By.CSS_SELECTOR, "input[type='file']")
    upload_trigger_xpath = (
        "//*[self::button or self::a or @role='button']["
        "contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'upload resume') "
        "or contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'update resume') "
        "or contains(translate(normalize-space(.),"
        "'ABCDEFGHIJKLMNOPQRSTUVWXYZ','abcdefghijklmnopqrstuvwxyz'), 'replace resume')]"
    )
    upload_pages = [
        'https://resume.naukri.com/cv-submission',
        'https://www.naukri.com/mnjuser/profile',
    ]

    for page_url in upload_pages:
        print(f'🔎 Looking for resume upload control at: {page_url}')
        driver.get(page_url)
        try:
            return WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located(file_input_locator)
            )
        except TimeoutException:
            # Some profile variants only render the file input after the user
            # activates an "Upload/Update Resume" control.
            triggers = driver.find_elements(By.XPATH, upload_trigger_xpath)
            for trigger in triggers:
                try:
                    if trigger.is_displayed() and trigger.is_enabled():
                        driver.execute_script('arguments[0].click();', trigger)
                        break
                except Exception:
                    continue
            try:
                return WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(file_input_locator)
                )
            except TimeoutException:
                print(f'⚠️ No file input at {driver.current_url}; page title: {driver.title!r}')

    raise TimeoutException(
        'Could not find Naukri resume upload input on the profile or resume-submission page.'
    )


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
            print('🔐 Detected an OTP challenge. Retrieving a new 6-digit email OTP...')
            otp_code = fetch_naukri_otp(expected_length=OTP_LENGTH)

            if otp_code is None:
                raise RuntimeError('Failed to extract OTP from email body.')

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

        try:
            wait.until(EC.any_of(
                EC.url_contains('mnjuser/profile'),
                EC.presence_of_element_located((By.XPATH, "//input[@type='file']")),
                EC.presence_of_element_located((By.XPATH, "//a[contains(@href,'/mnjuser/profile') or contains(text(),'My Naukri')]") )
            ))
        except TimeoutException:
            pass

        otp_inputs_after = find_otp_inputs(driver)
        if otp_inputs_after and 'mnjuser/profile' not in driver.current_url.lower():
            raise RuntimeError('Naukri login still requires OTP/verification after submission. The form may need manual intervention.')

        if 'mnjuser/profile' not in driver.current_url.lower() and 'login' in driver.current_url.lower():
            raise RuntimeError('Naukri login did not complete successfully. Check credentials or page behavior.')

        print("✅ Logged in successfully.")
        time.sleep(2)

        # Step 5: Open the resume-management UI and upload the latest resume.
        upload_input = find_resume_upload_input(driver)
        upload_input.send_keys(str(RESUME_PATH))
        wait_for_upload_confirmation(driver)
        print("✅ Resume uploaded successfully!")

        send_success_email()


    except Exception as e:
        print("❌ Error occurred:", e)
        print(traceback.format_exc())
        try:
            ARTIFACTS_DIR.mkdir(exist_ok=True)
            driver.save_screenshot(str(ARTIFACTS_DIR / 'error.png'))
            with open(ARTIFACTS_DIR / 'error_page.html', 'w', encoding='utf-8') as f:
                f.write(driver.page_source)
        except Exception:
            pass
        raise
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
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
            server.send_message(msg)
        print("📧 Success email sent!")
    except Exception as e:
        print("❌ Failed to send email:", e)

# ==== 🔁 Run It ====
if __name__ == "__main__":
    try:
        upload_resume()
    except Exception as e:
        print("❌ Exited with error:", e)
        sys.exit(1)
