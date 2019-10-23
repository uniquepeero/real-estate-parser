from selenium import webdriver
from time import sleep
import logging
import os
import requests
import configparser

path_to_driver = f'{os.getcwd()}\\geckodriver.exe'

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
fh = logging.FileHandler("parser_log.log", 'w', encoding="utf-8")
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
fh.setFormatter(formatter)
log.addHandler(fh)

driver = webdriver.Firefox(executable_path=path_to_driver)

def parseavito():
	try:
		url = "AVITOURL"
		driver.implicitly_wait(30)
		log.debug('Loading avito page...')
		driver.get(url)
		log.debug('Loaded.')
		sleep(3)
	except Exception as e:
		log.error(e)

	titles_dict = {}
	while True:
		try:
			titles = driver.find_elements_by_class_name('item-description-title-link')
			break
		except:
			pass
	for title in titles:
		titles_dict[title.text] = title.get_attribute('href')

	while True:
		sleep(5)
		newtitles_dict = {}
		driver.refresh()
		while True:
			try:
				newtitles = driver.find_elements_by_class_name('item-description-title-link')
				break
			except:
				pass
		for newtitle in newtitles:
			newtitles_dict[newtitle.text] = newtitle.get_attribute('href')

		msg = """"""
		for name, href in newtitles_dict.items():
			if name not in titles_dict.keys():
				log.debug(f'Found new: {name}')
				log.debug(f'href: {href}')
				msg += f'{name}\n{href}\n\n'
		if len(msg) > 1:
			send(msg)

		titles_dict = newtitles_dict

def send(message):
	proxies = {
		'http': '',
		'https': ''
	}
	url = f'https://api.telegram.org/botTOKEN/sendMessage?chat_id=CHATID&text={message}'
	try:
		res = requests.get(url, proxies=proxies)
		if res.status_code == requests.codes.ok:
			log.debug(f'Message sended {message}')
		else:
			log.error(f'Failed TG send: {res.status_code}')
	except requests.exceptions.RequestException:
		log.error('Failed TG send', exc_info=True)
	except ValueError:
		log.error(f'Failed TG sent: {res.text}')


if __name__ == '__main__':
    parseavito()

