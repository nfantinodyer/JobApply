#Do not remove the following comments
# config.json has the OpenAI API key
# files/CV.txt contains my cover letter that I sent to a game development company and I like how it is written.
# You can use this as a base for your cover letter, and have o3-mini generate a new one based on the job description.
# files/FullResume.pdf is my resume I need sent to the job application.
# I also would like to have my linkedin profile link included in the application.
# files/links/LinkedIn.txt contains my LinkedIn profile link.
# files/links/github.txt contains my GitHub profile link.
# files/links/portfolio.txt contains my portfolio link.

import os
import json
import openai
import time
import sys

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service

# ----------------------------------------------------------------------------
# 1. Load configuration and read local files
# ----------------------------------------------------------------------------

# Load API key from config.json
with open("config.json", "r", encoding="utf-8") as f:
    config = json.load(f)

openai.api_key = config["api_key"]

# Read your existing cover letter style (from files/CV.txt)
try:
    with open("files/CV.txt", "r", encoding="utf-8") as f:
        old_cover_letter_text = f.read().strip()
except FileNotFoundError:
    old_cover_letter_text = " "

# Read your LinkedIn, GitHub, and portfolio links
try:
    with open("files/links/LinkedIn.txt", "r", encoding="utf-8") as f:
        linkedin_url = f.read().strip()
except FileNotFoundError:
    linkedin_url = ""

try:
    with open("files/links/github.txt", "r", encoding="utf-8") as f:
        github_url = f.read().strip()
except FileNotFoundError:
    github_url = ""

try:
    with open("files/links/portfolio.txt", "r", encoding="utf-8") as f:
        portfolio_url = f.read().strip()
except FileNotFoundError:
    portfolio_url = ""

# ----------------------------------------------------------------------------
# 2. Generate a cover letter using o3-mini, referencing your old letter style
# ----------------------------------------------------------------------------

def generate_cover_letter(job_title, company_name, job_description, base_resume_text):
    """
    Use OpenAI (model=o3-mini) to generate a short, professional cover letter 
    for a specified job. Incorporate your old cover letter style, user experience,
    and links to LinkedIn, GitHub, and portfolio.
    """
    prompt = (
        f"You are an AI generating a concise, professional cover letter for the position '{job_title}' at '{company_name}'.\n\n"
        f"Job description:\n{job_description}\n\n"
        "Below is a sample cover letter the user likes the style of:\n"
        f"{old_cover_letter_text}\n\n"
        "User's relevant experience:\n"
        f"{base_resume_text}\n\n"
        "Instructions:\n"
        "- Match the user's style from the sample.\n"
        "- Highlight how the experience aligns with the job requirements.\n"
        "- End with a brief mention of the user's LinkedIn, GitHub, and portfolio.\n"
        "- Be direct and clear. Do not include placeholder text.\n"
    )

    try:
        response = openai.chat.completions.create(
            model="o3-mini",
            messages=[{"role": "user", "content": prompt}],
            max_completion_tokens=350,
        )
        cover_letter = response.choices[0].message.content
        
        # Append links to the end, if they exist
        final_cover_letter = cover_letter
        if linkedin_url or github_url or portfolio_url:
            links_section = "\n\nYou can also review my profiles here:\n"
            if linkedin_url:
                links_section += f"- LinkedIn: {linkedin_url}\n"
            if github_url:
                links_section += f"- GitHub: {github_url}\n"
            if portfolio_url:
                links_section += f"- Portfolio: {portfolio_url}\n"
            final_cover_letter += links_section

        return final_cover_letter

    except Exception as e:
        print("Error calling OpenAI:", str(e))
        return "Error generating cover letter"

# ----------------------------------------------------------------------------
# 3. Create a Selenium WebDriver
# ----------------------------------------------------------------------------

def create_webdriver(chromedriver_path=None, headless=False):
    """
    Create and return a Chrome WebDriver instance. 
    - If chromedriver_path is None, assume it's on PATH or in the same folder.
    - If headless=True, runs Chrome in headless mode (no visible browser).
    """
    options = webdriver.ChromeOptions()

    if headless:
        options.add_argument("--headless")
        options.add_argument("--disable-gpu")

    if chromedriver_path is None:
        # If update.ps1 places chromedriver in a known location,
        # we assume it's either on PATH or in the default scripts directory.
        service = Service()
    else:
        service = Service(chromedriver_path)

    driver = webdriver.Chrome(service=service, options=options)
    driver.maximize_window()
    return driver

# ----------------------------------------------------------------------------
# 4. Apply to a Job
# ----------------------------------------------------------------------------

def apply_to_job(
    driver,
    job_url,
    full_name,
    email,
    phone,
    resume_path,
    cover_letter_text=None
):
    """
    Navigate to a job posting, fill in the fields, and submit the application.
    Customize By selectors, XPaths, or CSS selectors to match the target site.
    """

    # A. Go to the job listing page
    driver.get(job_url)

    # B. Find the 'Apply' or 'Apply Now' button
    try:
        apply_button = driver.find_element(By.XPATH, "//button[contains(text(),'Apply')]")
        apply_button.click()
    except Exception as e:
        print("Could not find 'Apply' button:", e)
        return


    # C. Fill out form fields (customize for your site)
    try:
        name_field = driver.find_element(By.NAME, "name")
        name_field.clear()
        name_field.send_keys(full_name)

        email_field = driver.find_element(By.NAME, "email")
        email_field.clear()
        email_field.send_keys(email)

        phone_field = driver.find_element(By.NAME, "phone")
        phone_field.clear()
        phone_field.send_keys(phone)
    except Exception as e:
        print("Error filling personal info fields:", e)
        return


    # D. Upload Resume (typical input type="file")
    try:
        resume_upload = driver.find_element(By.NAME, "resume")
        resume_upload.send_keys(resume_path)
    except Exception as e:
        print("Error uploading resume:", e)
        return

    time.sleep(1)

    # E. Fill or Upload Cover Letter (if required)
    if cover_letter_text:
        try:
            cover_letter_field = driver.find_element(By.NAME, "cover_letter")
            cover_letter_field.clear()
            cover_letter_field.send_keys(cover_letter_text)
        except Exception as e:
            print("Error filling cover letter:", e)
            # Fallback if the site requires a file instead:
            # cover_letter_upload = driver.find_element(By.ID, "cover_letter_upload")
            # cover_letter_upload.send_keys("path\\to\\cover_letter.docx")
            pass

    time.sleep(1)

    # F. Submit Application
    try:
        submit_button = driver.find_element(By.CSS_SELECTOR, "button.submit")
        submit_button.click()
    except Exception as e:
        print("Error submitting application:", e)
        return

    time.sleep(5)  # Wait for confirmation or next page

    print("Application submitted successfully for:", job_url)

# ----------------------------------------------------------------------------
# 5. Main Routine / Example Usage
# ----------------------------------------------------------------------------

if __name__ == "__main__":
    # A. (Optional) Update ChromeDriver first
    # os.system('powershell.exe -ExecutionPolicy Bypass -File update.ps1')

    # B. Create a WebDriver instance
    driver = create_webdriver(
        chromedriver_path=None,  # or specify exact path if needed
        headless=False
    )

    # Example placeholders — adjust as needed:
    job_title = "Unity/C# Game Developer"
    company_name = "Digital Extremes"
    job_description = (
        "We are seeking a Junior to Mid-level Unity/C# Developer who is passionate about game design, "
        "has strong debugging skills, and the ability to collaborate in a team environment. "
        "Experience with published titles is a plus."
    )

    # This “base_resume_text” is a condensed version of your actual résumé details.
    base_resume_text = (
        "SUMMARY:\n"
        "Project Manager with a Bachelor's in Computer Science (2024) and currently pursuing a Master's (2025). "
        "Over one year of experience managing migration projects, researching, testing, troubleshooting, and providing IT support. "
        "Experience developing mobile games using Unity/C#, deploying to Google Play, implementing custom MIPS instructions, "
        "analyzing performance metrics, and automating data collection. Familiar with Linux, Windows, Cloudflare Workers, "
        "Grafana, and managing project timelines.\n\n"
        "PROJECT HIGHLIGHTS:\n"
        "- Gunslinger (Unity/C#): Published on Google Play Store; led design and iteration.\n"
        "- Q-Learning Maze Simulation (Unity/C#): Used A*; won Senior Capstone 1st place.\n"
        "- Linux vs Windows Energy Efficiency Research: Analyzed CPU usage and anomalies.\n"
        "- Cloudflare Worker Automation: Integrated with Grafana for real-time data.\n"
        "- MIPS Custom Instruction: Designed CPU datapath enhancements.\n\n"
        "WORK EXPERIENCE:\n"
        "- Project Manager/ERP Developer: Migrated from Ellucian Banner 8 to 9; COBOL scripts to SQL.\n"
        "- Dental Assistant/Receptionist: Provided office IT support, trained employees, aided staff.\n\n"
        "SKILLS:\n"
        "Java, JavaScript, Python, C/C++, C#, SQL, Linux, UML, Cloudflare Workers, Grafana, Android Studio. "
        "Also skilled in automation, testing, debugging, virtualization, containerization.\n"
    )

    # Generate a cover letter
    cover_letter = generate_cover_letter(job_title, company_name, job_description, base_resume_text)

    # Use the real path to your PDF resume (files/FullResume.pdf).
    resume_path = os.path.abspath("files/FullResume.pdf")

    # Apply to the job (point to your test form or actual job URL)
    apply_to_job(
        driver=driver,
        job_url="http://127.0.0.1:5500/test_form.html",
        full_name="Nicholas Fantino-Dyer",
        email="nfantinodyer@scu.edu",
        phone="(408)821-5157",
        resume_path=resume_path,
        cover_letter_text=cover_letter
    )

    # Close the browser
    driver.quit()
    print("Done.")
