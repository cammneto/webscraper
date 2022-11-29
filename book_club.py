from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.by import By
from selenium import webdriver
from bs4 import BeautifulSoup
from tabulate import tabulate
import pandas as pd
import re
import os
url = 'http://books.toscrape.com/'

# create a new Firefox session
options = Options()
options.headless = True
driver = webdriver.Firefox(options=options)
driver.implicitly_wait(1)
driver.get(url)

python_button = driver.find_element(By.XPATH,'/html/body/div/div/div/aside/div[2]/ul/li/a')
python_button.click() #click books menu
soup=BeautifulSoup(driver.page_source, 'lxml')
books = soup.find_all('ul', class_="nav nav-list") #get the categories list
categories_list = books[0].text
categories1 = categories_list.split('\',')[0].split('\n\n\n\n')
'''
Create a dictionary for books data storage
'''

df = {'Title':[], 'Genre':[], 'Stars':[], 'Price':[], 'In Stock':[], 'Stock #':[],}
for i in range(1,len(categories1)):
    category_button = driver.find_element(By.XPATH,'/html/body/div/div/div/aside/div[2]/ul/li/ul/li['+str(i)+']/a')
    print('--- Genre: ', category_button.text,'\n')
    category = category_button.text
    category_button.click()
    page = 2
    book=1
    while book <= 21:
        if book == 21:
            try:
                page_button = driver.find_element(By.PARTIAL_LINK_TEXT,'next')
                page_button.click()
                print('\n', 'page: ', page, '\n')
                page+=1
                book = 1
            except:
                break
        else:
            try:
                book_button = driver.find_element(By.XPATH,'/html/body/div/div/div/div/section/div[2]/ol/li['+str(book)+']/article/h3/a')
                print('Book #', book)
                book_button.click()
                soup=BeautifulSoup(driver.page_source, 'lxml')
                book_info = driver.find_element(By.XPATH,'/html/body/div/div/div[2]/div[2]/article/div[1]/div[2]/h1')
                print('Title: ', book_info.text)
                df['Title'].append(str(book_info.text))
                df['Genre'].append(str(category))
                html_table = soup.find_all('table')[0]
                table = pd.read_html(str(html_table))[0]
                df['Price'].append(str(table[1][2]))
                if 'In stock' == str(table[1][5][:8]):
                    df['In Stock'].append('yes')
                    try:
                        df['Stock #'].append(int(str(table[1][5])[-13:-11]))
                    except ValueError:
                        df['Stock #'].append(int(str(table[1][5])[-12]))
                else:
                    df['In Stock'].append('no')
                    df['Stock #'].append(int(0))
                mydivs =[p for p in soup.find_all('p', attrs={'class': re.compile('^star-rating.*')})]
                stars = str(mydivs[0]).split()[2]
                if stars == 'One">':
                    stars = 1
                elif stars == 'Two">':
                    stars = 2
                elif stars == 'Three">':
                    stars = 3
                elif stars == 'Four">':
                    stars = 4
                elif stars == 'Five">':
                    stars = 5
                df['Stars'].append(stars)
                driver.back()
                book+=1
            except:
                break
driver.quit()

df = pd.DataFrame(df)

#convert the pandas dataframe to JSON
json_records = df.to_json(orient='records')

#pretty print to CLI with tabulate and converts to an ascii table
print(tabulate(df, headers=["Book Name","Category","Stars","Price", "In Stock", "Stock #"],tablefmt='psql'))

#get current working directory
path = os.getcwd()
#open, write, and close the file
f = open(path + "\\books_database.json","w")
f.write(json_records)
f.close()
