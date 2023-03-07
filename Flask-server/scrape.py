from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager

from scrape_util import scrape_amazon_product_from_rows, scrape_amazon_categories_from_rows, scrape_alibaba_product_from_rows, scrape_alibaba_supplier_from_rows


def intial_config():

    ua = UserAgent()
    user_agent = ua.random

    options = Options()
    options.add_argument("--headless")
    options.add_argument(f'user-agent={user_agent})')
    # add incognito mode to options
    options.add_argument("--incognito")

    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()),
                              options=options)

    print(options.arguments)
    print("----------------------------------------")

    # simulate headless mode by minimizing the window
    driver.set_window_size(1366, 768)
    #driver.set_window_position(-2000, 0)
    return driver


def find_product_list(url, user_input):

    driver = intial_config()

    #load page with beautiful soup
    driver.get(url)
    #driver.get_screenshot_as_file("screenshot1.png")

    # find the search bar and enter the input
    driver.find_element(By.ID, "twotabsearchtextbox").send_keys(user_input)
    # click the search button
    driver.find_element(By.ID, "nav-search-submit-button").click()

    soup = BeautifulSoup(driver.page_source, "html.parser")

    # find all the search results on single page
    output = soup.find_all('div', {'data-component-type': 's-search-result'})

    # wait 1 second for the page to load
    driver.implicitly_wait(1)

    categories = scrape_amazon_categories_from_rows(soup)

    scraped_items = []
    # find the data from the search results
    for row in output:
        asin, title, img, price, rating, rating_count, link = scrape_amazon_product_from_rows(
            url, row)

        data = {
            "asin": asin,
            "title": title,
            "image": img,
            "price": price,
            "rating": rating,
            "rating_count": rating_count,
            "link": link,
            "categories": categories
        }
        scraped_items.append(data)

    total_items = len(scraped_items)
    driver.quit()
    return {"products": scraped_items, "item_count": total_items}


def find_suppliers_list(input_term):
    driver = intial_config()

    driver.get("https://alibaba.com")

    driver.find_element(
        By.XPATH,
        '//*[@id="J_SC_header"]/header/div[3]/div/div/div[2]/div/div[1]/div/input'
    ).send_keys(input_term)

    # click the input field to submit the search query
    driver.find_element(
        By.XPATH,
        '//*[@id="J_SC_header"]/header/div[3]/div/div/div[2]/div/div[1]/div/button'
    ).click()

    output = driver.find_element(By.CSS_SELECTOR,
                                 ".organic-list.app-organic-search__list")

    output2 = output.find_elements(By.CSS_SELECTOR,
                                   ".J-offer-wrapper.traffic-product-card")

    scraped_items = []

    # this i will generate a unique id for each product
    i = 0
    output2 = output2[:min(15, len(output2))]
    for row in output2:
        supplier_info = scrape_alibaba_supplier_from_rows(row, driver)
        if len(supplier_info) == 0 or len(supplier_info) < 2:
            continue
        products_info = scrape_alibaba_product_from_rows(row)

        data = {"id": i, "product": products_info, "supplier": supplier_info}
        scraped_items.append(data)
        i += 1

    driver.quit()

    return {"item_count": len(scraped_items), "results": scraped_items}


def find_suppliers_details(url):
    driver = intial_config()
    driver.get(url)

    soup = BeautifulSoup(driver.page_source, "html.parser")

    return ""