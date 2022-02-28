import unittest
import time
import argparse
import sys
import os
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options



parser = argparse.ArgumentParser(description='Weblogic Server Status Test')
parser.add_argument('-u', '--url', help='Input a stand URL with a port. Example http://stand-test.otr.ru:8889')
parser.add_argument('-l', '--login', help='Input a Login')
parser.add_argument('-p', '--password', help='Input a Password')
args = parser.parse_args()

chrome_options = Options()                                                                                                 
chrome_options.add_argument("--ignore-certificate-errors")                                                                 
#chrome_options.add_argument("--incognito")
#chrome_options.add_argument("--headless")

platform = sys.platform[0]
if platform == 'w':
    driver = webdriver.Chrome(os.path.dirname(os.path.abspath(__file__)) + '\\chromedriver.exe', options=chrome_options)
else:
    from pyvirtualdisplay import Display
    driver = webdriver.Chrome(os.path.dirname(os.path.abspath(__file__)) + '/chromedriver', options=chrome_options)
    display = Display(visible=0, size=(1024, 768))
    display.start()


class Weblogic(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = driver
        cls.url = args.url
        cls.login = args.login
        cls.password = args.password
        cls.port = args.url.split(":")[-1]
        cls.stand_path = args.url.rsplit(":", 1)[0]
        cls.driver.get(cls.stand_path + ":7001/console")
        input_login = cls.driver.find_element_by_id('j_username')
        input_login.send_keys(cls.login)
        input_password = cls.driver.find_element_by_id('j_password')
        input_password.send_keys(cls.password)
        input_password.send_keys(Keys.ENTER)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def setUp(self):
        self.startTime = time.time()
        self.driver.get(self.stand_path + ":7001/console")
        self.driver.find_element_by_partial_link_text('Home').click()

    def tearDown(self):
        t = time.time() - self.startTime
        print('%s: %.3f' % (self.id(), t))

    def test_0_login_window(self):
        self.driver.get(self.url + '/sufdclient/index.zul')
        self.driver.find_elements_by_link_text('Веб-клиент: Регистрация')

    def test_1_server(self):
        self.driver.find_element_by_link_text('Servers').click()
        id_list = self.driver.find_elements_by_tag_name('td')
        for id in id_list:
            if id.text == self.port:
                server_id = (id.get_attribute('id'))[10:]
                server_name = self.driver.find_element_by_id('name' + server_id).text
        self.assertEqual(self.driver.find_element_by_id('health' + server_id).text,  ' OK')
        self.assertEqual(self.driver.find_element_by_id('state' + server_id).text,  'RUNNING')

    def test_2_deployments(self):
        self.driver.find_element_by_link_text('Deployments').click()
        deployments_id_list = self.driver.find_elements_by_tag_name('td')
        for id in deployments_id_list:
            if id.text == 'sufd-server':
                deployments_server_id = (id.get_attribute('id'))[4:]
            elif 'sufd.libs' in id.text:
                deployments_libs_id = (id.get_attribute('id'))[4:]
            elif id.text == 'sufd.stand.patch':
                deployments_patch_id = (id.get_attribute('id'))[4:]
        self.assertEqual(self.driver.find_element_by_id('state' + deployments_server_id).text,  'Active')
        self.assertEqual(self.driver.find_element_by_id('health' + deployments_server_id).text,  ' OK')
        self.assertEqual(self.driver.find_element_by_id('state' + deployments_libs_id).text,  'Active')
        self.assertEqual(self.driver.find_element_by_id('state' + deployments_patch_id).text,  'Active')

    def test_3_bridge(self):
        self.driver.find_element_by_partial_link_text('Bridges').click()
        self.driver.find_element_by_id('name1').click()
        self.driver.find_element_by_partial_link_text('Monitoring').click()
        bridge_id_list = self.driver.find_elements_by_tag_name('td')
        for id in bridge_id_list:
            if id.text == 'WC_Portlet':
                bridge_id = (id.get_attribute('id'))[10:]
        self.assertEqual(self.driver.find_element_by_id('state' + bridge_id).text,  'Active')
        self.assertEqual(self.driver.find_element_by_id('description' + bridge_id).text, 'Forwarding messages.')

if __name__ == "__main__":
    runner = unittest.TextTestRunner()
    itersuite = unittest.TestLoader().loadTestsFromTestCase(Weblogic)
    runner.run(itersuite)