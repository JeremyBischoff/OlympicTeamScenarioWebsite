from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from selenium.common.exceptions import NoSuchElementException

def createGymnastData(driver):

    nationalTeamNames = ["Fuzzy Benas", "Jeremy Bischoff", "Cameron Bock", "Alex Diab", "Asher Hong", "Patrick Hoopes", "Paul Juda", "Brody Malone", "Yul Moldauer", "Stephen Nedoroscik", "Curran Phillips", "Fred Richard", "Colt Walker", "Donnell Whittenburg", "Shane Wiskus", "Khoi Young", "Tate Costa", "Joshua Karnes", "Kiran Mandava", "Kai Uemura"]

    gymnastData = []

    # to do day one and day two
    dayIDs = ['2','3']

    for dayID in dayIDs:
        gymnastDayData = {}

        numEvents = 6

        gymnastRank = 0

        while True:
            try:
                # get gymnast name
                gymnastNameID = f'[data-reactid=".0.0.2.0.1.2:${gymnastRank}.$name.1.0"]'.format(gymnastRank)
                gymnastName = driver.find_element(By.CSS_SELECTOR, gymnastNameID).text
                if gymnastName not in nationalTeamNames:
                    gymnastRank += 1
                    continue

                gymnastDayData[gymnastName] = []

                for event in range(numEvents):
                    try:
                        # ID w appropriate day id
                        gymnastEventScoreID = f'[data-reactid=".0.0.2.0.1.2:${gymnastRank}.$events.${event+1}.{dayID}.0"]'.format(gymnastRank, event+1)

                        gymnastEventScore = driver.find_element(By.CSS_SELECTOR, gymnastEventScoreID).text
                        num = float(gymnastEventScore)
                    except NoSuchElementException:
                        num = 0.0
                    gymnastDayData[gymnastName].append(num)

                gymnastRank += 1

            except NoSuchElementException:
                break

        gymnastData.append(gymnastDayData)

    return gymnastData

# scrapes data from a url
def scrapeData(url):

    maxRetries = 10

    for attempt in range(maxRetries):
        # Set up the Selenium WebDriver in headless mode
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        driver = webdriver.Chrome(options=options)
        driver.get(url)

        reactId = '[data-reactid=".0.0.2.0.1"]'

        try:
            # Wait for the specific element to be loaded
            wait = WebDriverWait(driver, 30)  # Increased the timeout to 20 seconds
            element = wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, reactId)))

            # Get the text content of the element
            htmlData = element.text
            if htmlData:
                #print(htmlData)
                break  # Exit loop if successful
            else:
                print("Retrying...")
                
        except Exception as e:
            print("An error occurred while waiting for the element:", e)
        

        if attempt < maxRetries - 1:
            time.sleep(5)
        else:
            print("Max retries reached, exiting.")

    return driver
    
