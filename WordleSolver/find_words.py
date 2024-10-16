from selenium import webdriver
from selenium.webdriver.edge.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time


# Set the path to the Edge WebDriver
#edge_driver_path = '..\Driver\msedgedriver.exe'  # e.g., r'C:\\path\\to\\msedgedriver.exe'
edge_driver_path = r'C:\Users\lucas\Documents\PersonalProjects\Weekly\WordleSolver\Driver\msedgedriver.exe'
print("\n\n" + edge_driver_path + "\n\n")

'''headless mode is busted
# Set options for headless mode
options = webdriver.EdgeOptions()
options.add_argument('headless')

# Create a new Edge session with headless options
driver = webdriver.Edge(service=Service(edge_driver_path), options=options)
'''

driver = webdriver.Edge()
#pretty sure this isnt needed
def open_webpage():
    try:
        # Open a webpage
        driver.get('https://www.thewordfinder.com/wordlist/')

        wait = WebDriverWait(driver, 10) 
        element = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div[2]/div/div[2]/div/section[2]/form/div/div/input')))
        element.click()
        element.send_keys(five_letters)
        element.send_keys('\n')
        
        element = wait.until(EC.presence_of_element_located((By.XPATH, '/html/body/div[1]/div[1]/div[2]/div/div[2]/div[1]/form/nav/a[2]')))
        element.click()
        
        time.sleep(100)
    
    finally:
        # Close the browser
        driver.quit()
    

def find_word_from_url(five_letters):
    try:
        # Open the webpage
        find_five_letter_words_website = f'https://www.thewordfinder.com/wordlist/words-containing-letters-{five_letters}/?dir=ascending&field=word&pg=1&size=5'
        driver.get(find_five_letter_words_website)

        # Wait for the span elements to be present
        wait = WebDriverWait(driver, 10)
        span_elements = wait.until(EC.presence_of_all_elements_located((By.XPATH, '/html/body/div[1]/div[1]/div[2]/div/div[2]/div[3]/ul/li[1]/a/span[1]')))

        # Extract the text content of each span element and concatenate to form the word
        word = ''.join([span.text for span in span_elements])

        print(f"Extracted word: {word}")



    finally:
        # Close the browser
        driver.quit()
        