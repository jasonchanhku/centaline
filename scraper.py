from selenium import webdriver
import requests
from bs4 import BeautifulSoup
import csv
import time
import pandas as pd

options = webdriver.ChromeOptions()
options.add_argument("--start-maximized")
# Uncomment when productionalized
# options.add_argument('--headless')
options.add_argument('window-size=2560,1440')


# Driver set up
url = "http://census.centamap.com/hong-kong"
driver = webdriver.Chrome("/Users/jasonchan/PycharmProjects/clp/centaline-scraping/chromedriver", options=options)
driver.get(url)
#driver.execute_script('chrome.settingsPrivate.setDefaultZoom(1.5);')

district_elements = driver.find_elements_by_css_selector('.district')

districts = [district.text.replace('District', '') for district in district_elements]

# get columns
data = requests.get(
    'http://census.centamap.com/hong-kong/Central%20and%20Western/CHMA/Kennedy-Town?field=t_pop&sort=default')

# load data into bs4 using html parser
# soup is entire html document
soup = BeautifulSoup(data.text, "html.parser")
col_names = ['District', 'Sub-District', 'Estate']

for col in soup.find_all('tr', {'class': 'tr-menu-item'})[0].find_all('a'):
    col_names.append(col.text)

col_full_names = []

for col in soup.find_all('tr', {'class': 'tr-menu-item'})[0].find_all('a'):
    for col_full in col.find_all('span'):
        col_full_names.append(col_full.text)

with open('centa_output.csv', 'w', newline='') as fp:
    f = csv.writer(fp)
    # print(headers)
    f.writerow(col_names)

    # len(districts)
    for i in range(len(districts)):
        # click on district
        driver.find_elements_by_css_selector('.district')[i].click()
        chma_elements = driver.find_elements_by_css_selector('.hma')
        chmas = [chma.text.replace('CHMA', '') for chma in chma_elements]
        #print(chmas)
        # len(chma_elements)

        for j in range(len(chma_elements)):
            if chmas[j] == 'Palm Springs / Fa...':
                continue
            driver.find_elements_by_css_selector('.hma')[j].click()
            # current url for potential bs4 scraping
            source = driver.page_source
            soup2 = BeautifulSoup(source, 'html.parser')

            total_buildings = len(soup2.find_all('a', {'class': 'building'}))

            for index, a in enumerate(soup2.find_all('a', {'class': 'building'})):

                row = []

                row.append(districts[i])
                row.append(chmas[j])
                row.append(a.find_all('span')[0].text)

                total_elems = len(soup2.find_all('tbody')[3].find_all('td'))
                data_elems = soup2.find_all('tbody')[3].find_all('td')
                n = 100
                # using list comprehension to break down chunks of data
                final = [data_elems[i * n:(i + 1) * n] for i in range((len(data_elems) + n - 1) // n)]

                for tabs in range(0, 100):
                    #print(soup2.find_all('tbody')[3].find_all('td')[tabs].text.strip().replace(',', ''))
                    row.append(final[index][tabs].text.strip().replace(',', ''))
                print(row)
                f.writerow(row)

            driver.find_element_by_css_selector('.grid-path:nth-child(2) a').click()

        driver.find_element_by_css_selector('.grid-path:nth-child(1) a').click()

    fp.close()
