import time
import argparse
import sys
import os
from pyzabbix import ZabbixMetric, ZabbixSender
from urllib.parse import urlparse
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

parser = argparse.ArgumentParser(description='Weblogic Server Status Test')
parser.add_argument('-u', '--url', help='Input a stand URL with a port. Example http://stand-test.otr.ru:8889')
parser.add_argument('-l', '--login', help='Input a Login')
parser.add_argument('-p', '--password', help='Input a Password')
args = parser.parse_args()

chrome_options = Options()                                                                                                 
chrome_options.add_argument("--ignore-certificate-errors")
chrome_options.add_argument("--headless")

platform = sys.platform[0]
if platform == 'w':
    driver = webdriver.Chrome(os.path.dirname(os.path.abspath(__file__)) + '\\chromedriver.exe', options=chrome_options)
else:
    driver = webdriver.Chrome(os.path.dirname(os.path.abspath(__file__)) + '/chromedriver', options=chrome_options)


wait = WebDriverWait(driver, 120)
ufos_url_stend = args.url
url = urlparse(ufos_url_stend)

if url.port == 8889:
    ufos_url = "http://" + url.netloc + "/sufdclient/index.zul"
else:
    ufos_url = "http://" + url.netloc
try:
    driver.get(ufos_url)
    start_time = time.time()
    driver.find_element(By.ID, "user").click()
    driver.find_element(By.ID, "user").send_keys(args.login)
    driver.find_element(By.ID, "psw").click()
    driver.find_element(By.ID, "psw").send_keys(args.password)
    driver.find_element(By.ID, "okButton").click()
    wait.until(expected_conditions.element_to_be_clickable((By.XPATH, "//span[contains(.,'Настройки')]")))
    login_time = time.time() - start_time
    driver.find_element(By.XPATH, "//span[contains(.,'Настройки')]").click()
    driver.find_element(By.XPATH, "//span[contains(.,'Выйти')]").click()
    exit_time = time.time() - start_time
    driver.quit()

    host = ((url.netloc).split(":")[0]).split(".")[0]
    total_time = int(login_time + exit_time)
    key = "login_test_" + str(url.port)
    zabbix_sender = ZabbixSender(zabbix_server='host.ru')
    metrics = []
    m = ZabbixMetric(host, key, total_time)
    metrics.append(m)
    zabbix_sender.send(metrics)
    print (host, url.port, total_time)
except Exception as error:
    print (url.netloc)
    print (error)
