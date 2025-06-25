from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
import pandas as pd
import time

# --- Configuration ---
search_query = "laptop"
max_pages = 3  # Set how many pages to scrape

# --- Setup Selenium ---
options = Options()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')
driver = webdriver.Chrome(options=options)

# --- Start Scraping ---
base_url = f"https://www.amazon.in/s?k=samsung+s25&crid=30NO9NEG0HWXT&sprefix=samsung+s25+%2Caps%2C514&ref=nb_sb_noss_2{search_query}"
driver.get(base_url)
time.sleep(3)

all_products = []
current_page = 1

while current_page <= max_pages:
    print(f"📄 Scraping Page {current_page}...")

    # Scroll to load content
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(2)

    soup = BeautifulSoup(driver.page_source, 'html.parser')
    products = soup.select('div.s-main-slot div[data-component-type="s-search-result"]')

    for product in products:
        title = product.select_one('h2 a span')
        price = product.select_one('.a-price-whole')
        rating = product.select_one('.a-icon-alt')
        link = product.select_one('h2 a')

        all_products.append({
            'Title': title.get_text(strip=True) if title else "N/A",
            'Price (INR)': price.get_text(strip=True) if price else "N/A",
            'Rating': rating.get_text(strip=True) if rating else "N/A",
            'Link': f"https://www.amazon.in{link['href']}" if link else "N/A"
        })

    # Try to click "Next" page
    try:
        next_button = driver.find_element(By.CSS_SELECTOR, 'a.s-pagination-next')
        if "disabled" in next_button.get_attribute("class"):
            print("🚫 No more pages.")
            break
        else:
            next_button.click()
            current_page += 1
            time.sleep(3)
    except:
        print("❌ Next button not found.")
        break

driver.quit()

# Save to CSV
df = pd.DataFrame(all_products)
df.to_csv("amazon_products_paginated.csv", index=False)
print(f"✅ Scraped {len(all_products)} products from {current_page} pages.")