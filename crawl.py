import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

def crawl_website(url):
    result = []

    # Set up Selenium with headless Chrome
    options = Options()
    options.add_argument("--headless")
    driver = webdriver.Chrome(options=options)

    # Base url without path
    base_url = urlparse(url).scheme + "://" + urlparse(url).netloc

    # Request the URL with Selenium
    driver.get(url)
    time.sleep(2)  # Give the page some time to load (adjust as needed)

    # Get the page source after ReactJS has rendered
    page_source = driver.page_source
    driver.quit()

    soup = BeautifulSoup(page_source, 'html.parser')

    links = soup.find_all('a')

    for link in links:
        href = link.get('href')

        # Check if a tag has href
        if not href:
            continue

        # Ignore hash links
        if href.startswith('#'):
            continue

        # If starts with /, append to base url
        if href.startswith('/'):
            absolute_url = urljoin(base_url, href)
            result.append(absolute_url)
            continue

        # If starts with http(s), append to result
        if href.startswith('http'):
            result.append(href)
            continue

        print("Unknown link: " + href)

    return result

