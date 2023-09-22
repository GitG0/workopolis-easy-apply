from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException
# from selenium.webdriver.chrome.service import Service
from selenium.webdriver.firefox.service import Service

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from bs4 import BeautifulSoup
import time
import json
import sqlite3
import re


class JobListing:
    def __init__(self, title, company, location, link, remote):
        self.title = title
        self.company = company
        self.location = location
        self.link = link
        self.remote = remote
        self.description = ""
        self.skills = ""
        self.benefits = ""

    def set_description(self, description):
        self.description = description

    def set_skills(self, skills):
        self.skills = skills

    def set_benefits(self, benefits):
        self.benefits = benefits

    def __str__(self):
        return (
            self.title
            + ", "
            + self.company
            + ", "
            + self.location
            + ", "
            + self.link
            + ", "
            + self.remote
            + ", "
            + self.description
            + ", "
            + self.skills
            + ", "
            + self.benefits
        )


def process_config():
    with open("config.json", "r") as jsonfile:
        config = json.load(jsonfile)
    return config


def launch_driver(url):
    service = Service()

    #chrome specific options
    # options = webdriver.ChromeOptions()
    # driver = webdriver.Chrome(service=service, options=options)

    #firefox specific options
    options = webdriver.FirefoxOptions()
    driver = webdriver.Firefox(service=service, options=options)

    driver.get(url)
    driver.refresh()
    return driver

def create_connection(db_file):
    try:
        conn = sqlite3.connect(db_file)
        return conn
    except Exception as e:
        print(e)

def search(driver, job, location):
    job_field = '//*[@id="query-input"]'
    location_field = '//*[@id="location-input"]'
    search_button = '/html/body/div[1]/div/main/section/div[1]/form/button'
    newest_toggle = '/html/body/div[1]/div/header/div[2]/div[1]/div/a[2]'
    
    driver.set_window_size(1080, 1080)

    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, job_field))).send_keys(job) # fill job title
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, location_field))).send_keys(location) # fill location
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, search_button))).click # find jobs button

    #sort by newest
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, newest_toggle))).click()

    return driver.current_url


def get_job_listings(driver):
    listings = []
    # driver.set_window_size(360, 640)
    scrollHeight = 0

    time.sleep(1)
    for i in range(0, 24):
        soup = BeautifulSoup(driver.page_source, "html.parser")
        listing = soup.find_all(
            "article", {"class": 'SerpJob'})[i]

        # scroll
        scrollHeight += 135.969
        driver.execute_script("window.scrollTo(0, " + str(scrollHeight) + ");")
        time.sleep(1)

        title = listing.find(
            "h2", {"class": 'SerpJob-title'}).text.strip()
        company = listing.find(
            class_='SerpJob-company').text.strip()
        location = listing.find(
            "span", {"class": 'SerpJob-location'}).text.strip()
        link = listing.find(
            "a", {"class": 'SerpJob-titleLink'})["href"].strip()
        salary = listing.find(
            "span", {"class": 'Salary'}).text.strip()
        remote = "Remote" if ("Remote" in location) else "Not Remote"

        listings.append(JobListing(
            title, company, location, link, remote))

    return listings


def apply(listing: JobListing, driver, db, connection):
    try:
        apply_to_listing(driver, listing)

        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "input-firstName"))).send_keys(first_name)
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "input-lastName"))).send_keys(last_name)
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "input-phoneNumber"))).send_keys(phone_number)
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "input-email"))).send_keys(email)
        # WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.XPATH, "input-location.city"))).send_keys(city) setup conditional

        for x in range(5):
            try:
                driver.find_element(
                    By.XPATH, "ia-continueButton").click()
            except:
                break

            resume = driver.find_element(By.XPATH, "ia-resumeUpload-title")
            if resume:
                resume.sendKeys(resume_location)
                continue

        try:
            db.execute("INSERT INTO listings (title, company, location, link, remote, description, skills, benefits) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (
                listing.title, listing.company, listing.location, listing.link, listing.remote, listing.description, listing.skills, listing.benefits))
            connection.commit()
            time.sleep(1)
        except Exception as e:
            print(e)
    except:
        pass
        


        # # next button loop
        # count = 0
        # for x in range(10):
        #     try:
        #         driver.find_element(
        #             By.XPATH, "//button[@aria-label='Continue to next step']").click()
        #         driver.find_element(
        #             By.XPATH, "//button[@aria-label='Continue to next step']").click()
        #     except:
        #         break

        #     # get form fields
        #     form = driver.find_element(
        #         By.CLASS_NAME, "jobs-easy-apply-modal")
        #     form_groups = form.find_elements(
        #         By.CLASS_NAME, "jobs-easy-apply-form-section__grouping")

        #     for group in form_groups:
        #         label = group.find_element(By.TAG_NAME, "label")
        #         select = input = textarea = None
        #         try:
        #             input = group.find_element(By.TAG_NAME, "input")
        #             if 'year' in label.text.lower() or 'how long' in label.text.lower():
        #                 input.clear()
        #                 input.send_keys("3")
        #                 continue
        #             elif input.get_attribute("type") == "radio":
        #                 input.click()
        #                 continue
        #             continue
        #         except:
        #             pass

        #         try:
        #             textarea = group.find_element(By.TAG_NAME, "textarea")
        #             # response = ask(label.text, listing.description, 4)
        #             textarea.send_keys(response)
        #             continue
        #         except:
        #             pass

        #         try:
        #             select = group.find_element(By.TAG_NAME, "select")
        #             select_label = select.accessible_name
        #             if "english" in select_label.lower():
        #                 continue
        #             options = select.find_elements(By.TAG_NAME, "option")
        #             options[1].click()
        #             continue
        #         except:
        #             pass

        #     try:
        #         driver.find_element(
        #             By.XPATH, "//button[@aria-label='Review your application']").click()
        #         time.sleep(1)
        #     except Exception as e:
        #         print(e)

        # try:
        #     driver.find_element(
        #         By.XPATH, "//button[@aria-label='Review your application']").click()
        #     time.sleep(1)
        # except Exception as e:
        #     print(e)

        # try:
        #     driver.find_element(
        #         By.XPATH, "//button[@aria-label='Submit application']").click()

        #     db.execute("INSERT INTO listings (title, company, location, link, description, easy_apply, remote) VALUES (?, ?, ?, ?, ?, ?, ?)", (
        #         listing.title, listing.company, listing.location, listing.link, listing.description, listing.easy_apply, listing.remote))
        #     connection.commit()
        #     time.sleep(1)
        # except Exception as e:
        #     print(e)
    # except:
    #     pass


def apply_to_listing(driver, listing):
    driver.get("https://www.workopolis.com" + listing.link)
    time.sleep(2)
    # driver.set_window_size(1080, 920)
    description = get_description(driver, listing)
    skills = get_skills(driver, listing)
    benefits = get_benefits(driver, listing)
    listing.set_description(description)
    listing.set_skills(skills)
    listing.set_benefits(benefits)
    try:
        driver.find_element(By.CLASS_NAME, '/html/body/div[1]/div/main/div/aside/header/div/div[2]/a').click()
    except NoSuchElementException:
        driver.back()


def get_description(driver, listing):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    description = soup.find(
        "div", {"class": "ViewJobBodyDescription"}).text.strip()
    return description

def get_skills(driver, listing):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    container = soup.find(
        "div", {"class": "viewjob-entities"})
    skills = container.findall('ul')
    return skills[0].text.strip()

def get_benefits(driver, listing):
    soup = BeautifulSoup(driver.page_source, "html.parser")
    container = soup.find(
        "div", {"class": "viewjob-entities"})
    benefits = container.findall('ul')
    return benefits[1].text.strip()

def next_page(driver, i, search_url):
    driver.set_window_size(1080, 920)
    # remove currentJobId parameter from url
    # url = search_url.split("currentJobId")[0]
    # https://www.linkedin.com/jobs/search/?currentJobId=3155175274&f_WT=2&keywords=Full%20Stack&refresh=true
    # remove currentJobId parameter from url using regex
    url = re.sub(r'&currentJobId=\d+', '', search_url)
    url = search_url + "&start=" + str(i*25)
    driver.get(url)


if __name__ == "__main__":
    driver = launch_driver("https://www.workopolis.com/en")
    config = process_config()

    job_titles = config["job_titles"]
    locations = config["locations"]
    connection = create_connection("workopolis_jobs.db")
    db = connection.cursor()

    # TODO add skills and benefits
    db.execute("CREATE TABLE IF NOT EXISTS listings (id INTEGER PRIMARY KEY, title TEXT, company TEXT, location TEXT, link TEXT, description TEXT, remote TEXT)")
    connection.commit()
    pages = 40
    time.sleep(3)

    for job in job_titles:
        for location in locations:
            time.sleep(2)
            search_url = search(driver, job, location)
            time.sleep(2)
            for i in range(1, pages + 1):
                try:
                    listings = get_job_listings(driver)
                except:
                    listings = []
                time.sleep(5)
                for listing in listings:
                    time.sleep(5)
                    apply(listing, driver, db, connection) #add config fields
                next_page(driver, i, search_url)
                time.sleep(5)
