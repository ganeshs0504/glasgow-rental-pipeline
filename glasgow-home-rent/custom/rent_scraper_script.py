import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
import pandas as pd
import time
from tqdm.auto import tqdm
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

if 'custom' not in globals():
    from mage_ai.data_preparation.decorators import custom
if 'test' not in globals():
    from mage_ai.data_preparation.decorators import test

xpaths = {
    'cookies_reject_btn': "//button[@id='onetrust-reject-all-handler']",
    'rent_listing': "//div[@class='l-searchResult is-list']",
    'address': ".//address",
    'price': ".//*[@class='propertyCard-priceValue']",
    'beds': ".//*[@class='property-information']/span[contains(@class, 'bed')]/following-sibling::span[1]",
    'bath': ".//*[@class='property-information']/span[contains(@class, 'bath')]/following-sibling::span[1]",
    'link': ".//div[@class='propertyCard-details']/a",
    'next_page': "//div[not(contains(@class, 'disabled'))]/button[@title='Next page']",
    'date_added': "//div[contains(text(), 'Added') or contains(text(), 'Reduced')]",
    'let_available_date': "//*[contains(text(), 'Let available date: ')]/..//dd",
    'deposit': "//*[contains(text(), 'Deposit')]/../dd",
    'furnish_type': "//*[contains(text(), 'Furnish type')]/..//dd",
    'property_type': "//*[@data-testid='svg-house']/../../span",
    'station_list': "//div[@id='Stations-panel']//li"
}

def fetch_listings(driver):
    data = []
    wait = WebDriverWait(driver, 5)
    wait.until(EC.visibility_of_element_located((By.XPATH, xpaths['rent_listing'])))
    item_list = driver.find_elements(By.XPATH, xpaths['rent_listing'])
    for ele in item_list:
        # webdriver.ActionChains(driver).move_to_element(ele).perform()
        link = ele.find_element(By.XPATH, xpaths['link']).get_attribute('href')
        address = ele.find_element(By.XPATH, xpaths['address']).text
        price = ele.find_element(By.XPATH, xpaths['price']).text
        try:
            beds = ele.find_element(By.XPATH, xpaths['beds']).text
        except Exception:
            beds = None
        try:
            bath = ele.find_element(By.XPATH, xpaths['bath']).text
        except Exception:
            bath = None
    
        data.append({
            'link': link,
            'address': address,
            'price': price,
            'beds': beds,
            'bath': bath
        })
    return data

def get_texts(driver, xpath):
    elements = driver.find_elements(By.XPATH, xpath)
    values = []
    for ele in elements:
        values.append(ele.text)
    return values

def scrape_listing_info(driver, link):
    driver.get(link)
    
    date_added = driver.find_element(By.XPATH, xpaths['date_added']).text.split()[-1]
    available_date = driver.find_element(By.XPATH, xpaths['let_available_date']).text
    deposit = driver.find_element(By.XPATH, xpaths['deposit']).text
    furnish_type = driver.find_element(By.XPATH, xpaths['furnish_type']).text
    try:
        property_type = driver.find_element(By.XPATH, xpaths['property_type']).text
    except Exception:
        property_type = None

    station_list = get_texts(driver, xpaths['station_list'])
    station_1 = station_list[0].split("\n")[0] if len(station_list) > 0 else None
    station_2 = station_list[1].split("\n")[0] if len(station_list) > 1 else None
    station_3 = station_list[2].split("\n")[0] if len(station_list) > 2 else None
    station_1_dist = station_list[0].split("\n")[-1] if len(station_list) > 0 else None
    station_2_dist = station_list[1].split("\n")[-1] if len(station_list) > 1 else None
    station_3_dist = station_list[2].split("\n")[-1] if len(station_list) > 2 else None

    return ({
        'date_added': date_added,
        'available_date': available_date,
        'deposit': deposit,
        'furnish_type': furnish_type,
        'property_type': property_type,
        'station_1': station_1,
        'station_1_dist': station_1_dist,
        'station_2': station_2,
        'station_2_dist': station_2_dist,
        'station_3': station_3,
        'station_3_dist': station_3_dist,
    })


@custom
def transform_custom(*args, **kwargs):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--no-sandbox')
    chrome_options.add_argument('--window-size=1920,1080')
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument('--headless')
    chrome_options.add_argument('--disable-gpu')
    driver = webdriver.Remote(command_executor='host.docker.internal:4444/wd/hub', options=chrome_options)

    url = 'https://www.rightmove.co.uk/property-to-rent/find.html?locationIdentifier=REGION%5E550&propertyTypes=&includeLetAgreed=false&mustHave=&dontShow=&furnishTypes=&keywords='

    driver.get(url)

    driver.find_element(By.XPATH, xpaths['cookies_reject_btn']).click()

    final_structured_listings = []
    while True:
        structured_listings = fetch_listings(driver)
        element = driver.find_element(By.XPATH, "//a[@title='Contact us']")
        webdriver.ActionChains(driver).move_to_element(element).perform()
        final_structured_listings.extend(structured_listings)
        try:
            wait = WebDriverWait(driver, 5)
            wait.until(EC.visibility_of_element_located((By.XPATH, xpaths['next_page'])))
            driver.find_element(By.XPATH, xpaths['next_page']).click()
        except Exception as e:
            print(e)
            print("Next button disabled: End of page")
            print("Exiting Script")
            break
        # time.sleep(2)

    df = pd.DataFrame(final_structured_listings)

    date_added = []
    available_date = []
    deposit = []
    furnish_type = []
    property_type = []
    station_1 = []
    station_1_dist = []
    station_2 = []
    station_2_dist = []
    station_3 = []
    station_3_dist = []

    for i, row in df.iterrows():
        scraped_data = scrape_listing_info(driver, row['link'])
        
        date_added.append(scraped_data['date_added'])
        available_date.append(scraped_data['available_date'])
        deposit.append(scraped_data['deposit'])
        furnish_type.append(scraped_data['furnish_type'])
        property_type.append(scraped_data['property_type'])
        station_1.append(scraped_data['station_1'])
        station_1_dist.append(scraped_data['station_1_dist'])
        station_2.append(scraped_data['station_2'])
        station_2_dist.append(scraped_data['station_2_dist'])
        station_3.append(scraped_data['station_3'])
        station_3_dist.append(scraped_data['station_3_dist'])


    driver.quit()

    df['date_added'] = date_added
    df['available_date'] = available_date
    df['deposit'] = deposit
    df['furnish_type'] = furnish_type
    df['property_type'] = property_type
    df['station_1'] = station_1
    df['station_1_dist'] = station_1_dist
    df['station_2'] = station_2
    df['station_2_dist'] = station_2_dist
    df['station_3'] = station_3
    df['station_3_dist'] = station_3_dist

    return df


@test
def test_output(output, *args):
    """
    Template code for testing the output of the block.
    """
    assert output is not None, "There is no output"
    # df = output['data']
    # assert len(output['date_added']) == df.shape[0], f"expected{df.shape[0]}; got{len(output['date_added'])}"
    # assert len(output['available_date']) == df.shape[0], f"expected{df.shape[0]}; got{len(output['available_date'])}"
    # assert len(output['deposit']) == df.shape[0], f"expected{df.shape[0]}; got{len(output['deposit'])}"
    # assert len(output['furnish_type']) == df.shape[0], f"expected{df.shape[0]}; got{len(output['furnish_type'])}"
    # assert len(output['property_type']) == df.shape[0], f"expected{df.shape[0]}; got{len(output['property_type'])}"
    # assert len(output['station_1']) == df.shape[0], f"expected{df.shape[0]}; got{len(output['station_1'])}"
    # assert len(output['station_1_dist']) == df.shape[0], f"expected{df.shape[0]}; got{len(output['station_1_dist'])}"
    # assert len(output['station_2']) == df.shape[0], f"expected{df.shape[0]}; got{len(output['station_2'])}"
    # assert len(output['station_2_dist']) == df.shape[0], f"expected{df.shape[0]}; got{len(output['station_2_dist'])}"
    # assert len(output['station_3']) == df.shape[0], f"expected{df.shape[0]}; got{len(output['station_3'])}"
    # assert len(output['station_3_dist']) == df.shape[0], f"expected{df.shape[0]}; got{len(output['station_3_dist'])}"
