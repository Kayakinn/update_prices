# Importing necessary libraries
import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import chromedriver_autoinstaller
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from git import Repo
import time

# Read the CSV file into a DataFrame
df = pd.read_csv('rush_ebay调查 - コミパラ.csv')

# Automatically install the chromedriver that matches the current version of chrome installed on your machine
chromedriver_autoinstaller.install()

# Set up the Selenium Chrome options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Ensures the browser window doesn't pop up

# Initialize the WebDriver
driver = webdriver.Chrome(options=chrome_options)

# Function to create search URL
def create_search_url(name, model, rarity):
    # Properly encode parameters to handle special characters
    return f"https://cardrush.media/onepiece/buying_prices?displayMode=リスト&limit=100&name={name}&rarity={rarity}&model_number={model}&amount=&page=1&sort%5Bkey%5D=amount&sort%5Border%5D=desc&associations%5B%5D=ocha_product&to_json_option%5Bexcept%5D%5B%5D=created_at&to_json_option%5Binclude%5D%5Bocha_product%5D%5Bonly%5D%5B%5D=id&to_json_option%5Binclude%5D%5Bocha_product%5D%5Bmethods%5D%5B%5D=image_source&display_category%5B%5D=最新弾&display_category%5B%5D=通常弾"

# Function to extract price from webpage
def extract_price(driver, name, model, rarity):
    # try:
    #     # Locate the table by its class
    price_table = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CSS_SELECTOR, ".IndexTemplate__StyledPriceTable-sc-1c0z7vg-2.gLkagS.PriceTable.onepiece"))
    )
    # Get all the rows in the table body
    rows = price_table.find_elements_by_css_selector("tbody > tr")
    #print(dir(rows),type(rows))
    for row in rows:
        # print(type(row),dir(row))
        # print(row)
        # Extract the name, model, and rarity from the row
        row_name = row.find_element_by_css_selector("td.name").text
        row_model = row.find_element_by_css_selector("td.model_number").text
        row_rarity = row.find_element_by_css_selector("td.rarity").text
        
        # Compare with the provided name, model, and rarity
        if name in row_name and model == row_model and rarity == row_rarity:
            # Extract the amount if the row matches
            price = row.find_element_by_css_selector("td.amount").text
            return price.strip().replace('¥', '').replace(',', '')
    # except Exception as e:
    #     print(f"An error occurred: {e}")
    return "Not Found"


# Iterate over the dataframe and update prices
for index, row in df.iterrows():
    search_url = create_search_url(row['カード名'], row['型番'], row['レアリティ'])
    #print(search_url)
    driver.get(search_url)
    price = extract_price(driver, row['カード名'], row['型番'], row['レアリティ'])
    df.at[index, 'カードラッシュ買取金額'] = price

# Save the updated DataFrame to a new CSV
updated_csv_path = 'updated_rush_ebay.csv'
df.to_csv(updated_csv_path, index=False)

# Commit and push the changes to the GitHub repository
repo = Repo('Users\theou\OneDrive\桌面\cardprice\cardrushprice')
repo.git.add(updated_csv_path)
repo.index.commit('Update prices')
origin = repo.remote(name='origin')
origin.push()

# Close the WebDriver
driver.quit()
