import csv
import paramaters
from parsel import Selector
from time import sleep, time
from selenium import webdriver
import requests
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import NoSuchElementException


def validate_field(field):
    if field:
        pass
    else:
        field = ''
    return field.strip()


start = time()
writer = csv.writer(open(paramaters.file_name, 'w'))
writer.writerow(['Name', 'Job Title', 'School', 'Location', 'URL'])

options = Options()
options.add_argument('--headless')
options.add_argument('--disable-gpu')
# options.add_argument(
#     "--user-agent=Mozilla/5.0 (compatible; MSIE 9.0; Windows Phone OS 7.5; Trident/5.0; IEMobile/9.0)"
# )
driver = webdriver.Chrome(chrome_options=options)

driver.get('https://www.linkedin.com')
username = driver.find_element_by_xpath('//form/input[@class="login-email"]')
username.send_keys(paramaters.linkedin_username)
sleep(.1)

password = driver.find_element_by_xpath('//form/input[@type="password"]')
password.send_keys(paramaters.linkedin_password)
sleep(.1)

submit = driver.find_element_by_xpath('//form/input[@type="submit"]')
submit.click()
sleep(.1)

driver.get('https://www.google.com/')
try:
    change_to_english = driver.find_element_by_xpath(
        '//a[contains(@href,"setprefs")]')
    change_to_english.click()
except NoSuchElementException:
    pass
query = driver.find_element_by_xpath('//input[@name="q"][@maxlength]')
query.send_keys(paramaters.search_query)
query.send_keys(Keys.RETURN)
number_of_pages = 0
number_of_developers = 0
while True:
    current_search_url = driver.current_url
    linkedin_urls = driver.find_elements_by_xpath('//cite[@class]')
    # print('len', len(linkedin_urls))
    linkedin_urls = [
        url.text for url in linkedin_urls if 'linkedin' in url.text
    ]
    for link in linkedin_urls:
        number_of_developers += 1
        print('number_of_developers', number_of_developers)
        driver.get(link)
        sleep(.2)
        sel = Selector(text=driver.page_source)
        height = driver.execute_script("return document.body.scrollHeight")
        current_height = 0
        while height >= current_height:
            # print(height)
            # print(current_height)
            current_height = height / 10 + current_height
            driver.execute_script(f"window.scrollTo(0, {current_height});")
        sleep(1)
        sel = Selector(text=driver.page_source)
        name = sel.xpath('//h1/text()').extract_first()
        job_title = sel.xpath('//h2/text()').extract_first()
        school_name = sel.xpath(
            '//div[@class="pv-entity__degree-info"]/h3/text()').extract_first(
            )
        location = sel.xpath(
            '//h3[starts-with(@class,"pv-top-card-section__location")]/text()'
        ).extract_first()
        name = validate_field(name)
        job_title = validate_field(job_title)
        school = validate_field(school_name)
        location = validate_field(location)
        linkedin_url = validate_field(link)
        writer.writerow([name, job_title, school, location, linkedin_url])
    try:
        driver.get(current_search_url)
        next_link_selector = '//a[@id="pnnext"]'
        next_link = driver.find_elements_by_xpath(next_link_selector)[0]
        active_page = driver.find_elements_by_xpath('//td[@class="cur"]/span')[
            0]
        print('active_page', active_page.text)
        if next_link is None:
            break
        next_link.click()
    except IndexError:
        break
    print(number_of_pages)
    number_of_pages += 1
end = time()
print('time is', end - start)
print('number_of_pages', number_of_pages)
driver.quit()
