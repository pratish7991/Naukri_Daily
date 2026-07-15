
Generate an App Password if you're using Gmail (you can’t use your regular Gmail password due to security).

🔐 Step 1: Set Up App Password (once)
Go to: https://myaccount.google.com/apppasswords

Choose:

App: Mail

Device: Windows Computer

Copy the 16-digit password (keep it safe, treat like your password)

✅ Step 2: Update Your Script
Here’s how to send an email after successful upload:




✅ Here's Exactly How to Automate Your Script with Task Scheduler on Windows:
1. 🧠 Understand What You Need
You need Task Scheduler to run:

bash
Copy
Edit
<path_to_python.exe> <path_to_your_script.py>
In your case:

bash
Copy
Edit
c:\Users\hp\Desktop\Naukri\.venv\Scripts\python.exe c:\Users\hp\Desktop\Naukri\upload_resume.py
2. 🛠️ Step-by-Step Setup in Task Scheduler
📌 Open Task Scheduler
Press Win + S, type Task Scheduler, and open it.

➕ Create a Basic Task
Click “Create Basic Task”

Name it: Naukri Resume Upload

Trigger: Select Daily and set time (e.g., 10:00 AM)

⚙️ Action → Select Start a program
Program/script:

makefile
Copy
Edit
c:\Users\hp\Desktop\Naukri\.venv\Scripts\python.exe
Add arguments:

makefile
Copy
Edit
c:\Users\hp\Desktop\Naukri\upload_resume.py
Start in (optional but recommended):

makefile
Copy
Edit
c:\Users\hp\Desktop\Naukri
✅ Ensure all paths are correct and point to:

Python interpreter inside your .venv

The full path to your script

🧪 Final Step: Test it
Find the task in the list

Right-click → Run

If it runs correctly (browser opens and uploads resume), it's working
