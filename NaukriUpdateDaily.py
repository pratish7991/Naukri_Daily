from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# ==== 🔐 Your Credentials & File ====
NAUKRI_EMAIL = 'dpratishraj7991@gmail.com'
NAUKRI_PASSWORD = 'Bittu@7991'
RESUME_PATH = r'C:\Users\hp\Desktop\Naukri\PratishDewanganMLE.pdf' # Make sure this is correct

# ==== 🚀 Main Function ====
def upload_resume():
    # Set up Chrome driver
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(options=options)

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
        upload_input.send_keys(RESUME_PATH)
        print("✅ Resume uploaded successfully!")

        time.sleep(5)
        send_success_email()


    except Exception as e:
        print("❌ Error occurred:", e)
        driver.save_screenshot("error.png")
    finally:
        driver.quit()


def send_success_email():
    sender_email = "dpratishraj7991@gmail.com"             # The Gmail used to send the mail
    sender_app_password = "zcjordzxmcoiaemy"
    receiver_email = "dpratishraj7991@gmail.com"      # Your personal email

    subject = "✅ Naukri Resume Upload Success"
    body = "Hi Pratish,\n\nYour resume was successfully uploaded to Naukri.com.\n\nRegards,\nYour Automation Bot 🤖"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'plain'))

    try:
        server = smtplib.SMTP('smtp.gmail.com', 587)
        server.starttls()
        server.login(sender_email, sender_app_password)
        server.send_message(msg)
        server.quit()
        print("📧 Success email sent!")
    except Exception as e:
        print("❌ Failed to send email:", e)

# ==== 🔁 Run It ====
if __name__ == "__main__":
    if os.path.exists(RESUME_PATH):
        upload_resume()
    else:
        print(f"❌ Resume file not found at: {RESUME_PATH}")





