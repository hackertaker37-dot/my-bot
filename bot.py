from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import re

def get_available_numbers(country_code, combo_index=1, user_id=None):
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page()
            page.goto("https://freephonenum.com/fake-phone-number-generator", timeout=60000)
            page.wait_for_timeout(5000)
            content = page.content()
            browser.close()
            
            soup = BeautifulSoup(content, 'html.parser')
            numbers = []
            for element in soup.select('.phone-number'):
                num = re.sub(r'\D', '', element.text)
                if len(num) >= 7:
                    numbers.append(num)
            return list(set(numbers))[:10]
            
    except Exception as e:
        print(f"Error scraping site: {e}")
        return []
