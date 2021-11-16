import pandas as pd
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
from removeAccents import removeAccents
from selenium.common.exceptions import NoSuchElementException

chrome_options = Options()
chrome_options.add_argument("--headless")
path_do_diver = '/Users/kacperdzida/PycharmProjects/webscrape_PV/chromedriver'
driver = webdriver.Chrome(path_do_diver, options=chrome_options)

company_list = []
pause_time = 2  # Pause time was implemented to make sure, that sites loaded properly.

# Get content of the first list. Done separately as it has different url construction.
page = driver.get("https://gramwzielone.pl/baza-firm")
time.sleep(pause_time)
box = driver.find_element_by_xpath('//*[@id="gwz-content"]/div[1]/div[1]/div/span/span/div[4]')
company_list.append(box.text.split('\n')[1::3])
print('Companies from page 1 saved.')

# Get content of the remaining sites.
number_of_pages = 233  # number of pages should be defined before running the script

for page in range(2, number_of_pages+1):
    driver.get(f'https://www.gramwzielone.pl/baza-firm/35/fotowoltaika/strona/{page}')
    time.sleep(pause_time)
    data_box = driver.find_element_by_xpath('//*[@id="gwz-content"]/div[1]/div[1]/div/span/span/div[4]')
    company_list.append(data_box.text.split('\n')[1::3])
    print(f'Companies from page {page} saved.')

# Flatten the list of lists.
full_companies_list = [item for c_list in company_list for item in c_list]
# Remove duplicates.
full_companies_list = list(dict.fromkeys(full_companies_list))
print('List flattened, duplicated removed.')

# Turn list of company names to company urls.
company_urls = list(
    map(lambda company: removeAccents(company.replace('.', '').replace(' ', '-').replace('|', '').replace(',', '')
                                      .replace('&', '').replace('"', '').replace('®', '')
                                      .lower()), full_companies_list))
print('List of URLs created.')

company_data = []  # List to to store scraped data about company.
list_of_errors = []  # List to store companies that didn't load properly.

# Collect data
for company in company_urls:
    try:
        page = driver.get(f'https://gramwzielone.pl/baza-firm/35/fotowoltaika/{company}')
        time.sleep(pause_time)
        data_box = driver.find_element_by_xpath('//*[@id="gwz-content"]/div[1]/div[1]/div')
        company_data.append(data_box.text.split('\n')[:16])
        print(f'Data for company {company_urls.index(company)}. {company} collected.')
    except NoSuchElementException:
        list_of_errors.append(company)
        print(f'Error occurred for company: {company_urls.index(company)}. {company}.')

# Turn list of collected data into DataFrame
companies_df = pd.DataFrame(company_data)

companies_df.to_excel('baza.xlsx')
print('Database saved to Excel file.')