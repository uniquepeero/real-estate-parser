from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from dotenv import load_dotenv
import logging
import os
import requests
import re


path_to_driver = f'{os.getcwd()}\\geckodriver.exe'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fh = logging.FileHandler("parser.log", 'w', encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)

driver = webdriver.Firefox(executable_path=path_to_driver)

wait = WebDriverWait(driver, 60)

env_path = os.path.join(os.path.dirname(__file__), '.env')
if os.path.exists(env_path):
	load_dotenv(env_path)
else:
	log.error('.env file not found')

API_KEY = os.getenv('API_KEY')
CHAT_ID = os.getenv('CHAT_ID')


def parse_avito():
	url = "AVITOLINK"
	driver.implicitly_wait(30)
	log.debug('Loading avito page...')
	driver.get(url)
	log.debug('Loaded.')

	titles_dict = {}
	titles = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'item-description-title-link')))

	for title in titles:
		titles_dict[title.text] = title.get_attribute('href')

	while True:
		msg = """"""
		sleep(5)

		new_titles_dict = {}
		driver.refresh()
		new_titles = wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'item-description-title-link')))

		for new_title in new_titles:
			new_titles_dict[new_title.text] = new_title.get_attribute('href')

		for name, href in new_titles_dict.items():
			if name not in titles_dict.keys():
				log.debug(f'Found new: {name}')
				log.debug(f'href: {href}')

				driver.execute_script(f'window.open("{href}","_blank");')
				driver.switch_to.window(driver.window_handles[1])

				views = driver.find_element_by_xpath("//div[@class='title-info-metadata-item title-info-metadata-views']")
				views = re.search(r'(\d+)', views.text)
				views = int(views.group(0))

				if views < 200:
					msg += f'{name}\n{href}\n\n'
				else:
					log.debug(f'Too many views: {views}')

				driver.execute_script('window.close();')
				driver.switch_to.window(driver.window_handles[0])

		if msg:
			send(msg)
		titles_dict = new_titles_dict


def send(message):
	url = f'https://api.telegram.org/bot{API_KEY}/sendMessage?chat_id={CHAT_ID}&text={message}'
	try:
		res = requests.get(url)
		if res.status_code == requests.codes.ok:
			log.debug(f'Successful send: {message}')
		else:
			log.error(f'Send failed: {res.status_code}')
	except requests.exceptions.RequestException:
		log.error('Send failed', exc_info=True)
	except ValueError:
		log.error(f'Send failed: {res.text}')


if __name__ == '__main__':
	parse_avito()
