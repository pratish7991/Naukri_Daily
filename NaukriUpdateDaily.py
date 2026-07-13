from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import time
import os
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
RESUME_PATH = Path(os.environ.get('RESUME_PATH')).expanduser() if os.environ.get('RESUME_PATH') else Path.cwd() / 'PratishDewanganMLE.pdf'
RESUME_PATH = RESUME_PATH.resolve()
HEADLESS = os.environ.get('HEADLESS', '1') == '1'

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
    options.binary_location = '/Applications/Google Chrome.app/Contents/MacOS/Google Chrome'

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
        print("✅ Logged in successfully.")
        time.sleep(5)

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
        driver.save_screenshot("error.png")
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





