from pyvirtualdisplay import Display
from selenium import webdriver
from config import config
from mysql_wrapper import MySqlWrapper

datastore = MySqlWrapper()

if config['browser'] == 'firefox':
    browser = webdriver.Firefox()
elif config['browser'] == 'google-chrome':
    browser = webdriver.Firefox()

while url = datastore.next_page():
    #url = 'http://localhost:8000/test.html'
    browser.get(url)
    datastore.save_page(browser.page_source)
    datastore.add_paths(paths)

browser.close()
