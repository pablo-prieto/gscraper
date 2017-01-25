from selenium import webdriver                                                                      
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
import random

def start_google_session(search_term, start_on=0):
    driver = webdriver.Firefox()
    driver.get('http://www.google.com/')
    search_field = driver.find_element_by_name("q") 
    search_field.send_keys(search_term)
    search_field.submit()
    sleep(5)
    if start_on != 0:
        driver.get(driver.current_url + '&num=50&filter=0&start=%s' % start_on)
    else:
        driver.get(driver.current_url + '&num=50&filter=0')
    sleep(5)
    return driver

def get_results(driver):
    results = []
    div_results = driver.find_element_by_class_name("srg")
    h3_results = div_results.find_elements_by_class_name("r")
    for section in h3_results:                                                        
        a = section.find_element_by_tag_name("a") 
        href = a.get_attribute("href")
        print(href)
        results.append(href)
    return results

def get_next_page(driver, return_object=False):
    nav_table = driver.find_element_by_id("nav")
    next_page_td = nav_table.find_elements_by_tag_name("td")[-1]
    next_page_a = next_page_td.find_element_by_tag_name("a")
    next_page = next_page_a.get_attribute("href")
    if return_object is False:    
        return next_page + '&num=50&filter=0'
    else:
        return next_page_a

def scrape(search_term, min_rest=1, max_sleep=10, start_on=0):
    driver = start_google_session(search_term)
    print("Session started")
    results = []
    next_page = ""
    cont = True
    while cont is True:
        try:
            if next_page == get_next_page(driver):
                cont = False
            print("FETCHING..." )
            results += get_results(driver)
            print("FETCHED %s RESULTS SO FAR." % len(results))
            next_page = get_next_page(driver)
            print("LOADING NEXT PAGE")
            driver.get(next_page)
            sleep(3)
        except Exception:
            response = int(input("Exception catched. Continue (1) or Return (2)?\n"))
            if response == 1:
                continue
            if response == 2:
                return results, driver
    return results, driver
       
