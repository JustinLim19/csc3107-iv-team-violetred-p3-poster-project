from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time
import pandas as pd

def select_dropdown_item(dropdown_id, item_text):
    """ Helper function to handle dropdown selection with retries for stale elements. """
    attempt = 0
    max_attempts = 3
    while attempt < max_attempts:
        try:
            wait.until(EC.element_to_be_clickable((By.ID, dropdown_id))).click()
            item = wait.until(EC.visibility_of_element_located((By.XPATH, f"//a[text()='{item_text}']")))
            item.click()
            return True
        except Exception as e:
            print(f"Retrying dropdown selection: {e}")
            attempt += 1
            time.sleep(2)
    print(f"Failed to select {item_text} from dropdown {dropdown_id}, skipping to next.")
    return False

# Setup Chrome WebDriver
service = Service(ChromeDriverManager().install())
driver = webdriver.Chrome(service=service)

# URL to open
url = 'http://www.weather.gov.sg/climate-historical-daily/'

# Open the URL in Chrome
driver.get(url)
wait = WebDriverWait(driver, 10)

months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
locations = [
    "Admiralty", "Ang Mo Kio",
    "Botanic Garden", "Bukit Panjang", "Bukit Timah", "Buona Vista",
    "Changi", "Choa Chu Kang (Central)", "Choa Chu Kang (South)", 
    "Clementi", "Dhoby Ghaut", "East Coast Parkway", 
    "Jurong (West)", "Jurong Island", "Jurong Pier",
    "Kent Ridge", "Kranji Reservoir", "Lim Chu Kang",
    "Lower Peirce Reservoir", "Macritchie Reservoir", "Mandai", "Marina Barrage", 
    "Marine Parade", "Newton", "Nicoll Highway", "Pasir Panjang", "Pasir Ris (Central)",
    "Pasir Ris (West)", "Paya Lebar", "Pulau Ubin", "Punggol", "Queenstown", "Seletar",
    "Semakau Island", "Sembawang", "Sentosa Island", "Serangoon", 
    "Simei", "Somerset (Road)", "Tai Seng", "Tanjong Katong", "Tengah",
    "Toa Payoh", "Tuas", "Tuas South", "Ulu Pandan", "Upper Peirce Reservoir",
    "Whampoa"
]
data_list = []

try:
    for location in locations:
        if select_dropdown_item('cityname', location):
            time.sleep(5)
            # Wait and click the year dropdown to show the year options and select 2023
            wait.until(EC.element_to_be_clickable((By.ID, 'year'))).click()
            wait.until(EC.element_to_be_clickable((By.XPATH, "//a[contains(@onclick, \"setMonth(2023)\")]"))).click()
            if select_dropdown_item('year', '2023'):
                time.sleep(5)  # Allow time for data to load
                for month in months:
                    if select_dropdown_item('month', month):
                        time.sleep(5)  # Allow time for data to load

                        display_button = wait.until(EC.element_to_be_clickable((By.ID, 'display')))
                        display_button.click()
                        time.sleep(5)  # Wait for the data to be displayed after clicking

                        table = wait.until(EC.presence_of_element_located((By.CLASS_NAME, 'table-calendar')))
                        rows = table.find_elements(By.TAG_NAME, 'tr')
                        for row in rows[1:]:  # Skip header row
                            cols = row.find_elements(By.TAG_NAME, 'td')
                            col_data = [col.text for col in cols]
                            if col_data:
                                data_list.append([location, month] + col_data)
finally:
    driver.quit()

df = pd.DataFrame(data_list, columns=['Location', 'Month', 'Date', 'Daily Rainfall Total (mm)', 'Highest 30-min Rainfall (mm)',
                                      'Highest 60-min Rainfall (mm)', 'Highest 120-min Rainfall (mm)', 'Mean Temperature (°C)',
                                      'Maximum Temperature (°C)', 'Minimum Temperature (°C)', 'Mean Wind Speed (km/h)', 
                                      'Max Wind Speed (km/h)'])

df.to_excel('C:/Users/NINO/Desktop/full_year_weather_data.xlsx', index=False)
