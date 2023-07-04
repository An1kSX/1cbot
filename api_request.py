from os import stat, listdir
from os.path import isfile, abspath, dirname, join
from db_functions import get_phone_number, get_mail, get_plea_info, get_plea_type
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime





get_plea_types_url = 'http://sd.softtech.uz/ServiceDesk/hs/STSAPI/download/RequestType' # запрос для получения типов заявок
post_plea_url = 'http://sd.softtech.uz/ServiceDesk/hs/STSAPI/upload/Request'            # запрос для отправки заявки
get_mails_url = 'http://sd.softtech.uz/ServiceDesk/hs/STSAPI/download/RequestDomenType' # запрос для получения доступных почт
post_photo_url = 'http://sd.softtech.uz/ServiceDesk/hs/STSAPI/upload/fileBin?fileName=' # запрос для отправки фото

api_login = 'Admin_Api'                                                                 # логин апи
api_password = '!QAZ2wsx'                                                               # пароль апи








def get_plea_types():
	try:
		types = requests.get(get_plea_types_url, auth = HTTPBasicAuth(api_login, api_password), timeout = 30)
		if types.status_code == 200:
			return types

		else:
			return types.text

	except Exception as e:
		return e


def get_mails():
	try:
		mails = requests.get(get_mails_url, auth = HTTPBasicAuth(api_login, api_password), timeout = 30)
		if mails.status_code == 200:
			return mails

		else:
			return mails.text

	except Exception as e:
		return e


def send_photo(photo, name):
	if len(name.replace('jpg', '')) != len(name):
		headers = {
			'Content-Type': 'image/jpeg',
			'Content-Disposition': 'attachment'
		}
	else:
		headers = {
			'Content-Type': 'image/png',
			'Content-Disposition': 'attachment'
		}

	try:
		payload = {}
		file = open(photo, 'rb').read()
		req = requests.request('POST', f'{post_photo_url}{name}',  data = file, headers = headers, auth = HTTPBasicAuth(api_login, api_password), timeout = 30)
		if req.status_code == 200:
			return req

		else:
			return req.text

	except Exception as e:
		return e



def send_plea_to_1c(user_id, plea_num):
	files = []
	now = datetime.now()
	path = dirname(abspath(__file__))
	path = join(path, f'{user_id}_{plea_num}')

	GUID_plea = get_plea_type(user_id)
	phone_number = get_phone_number(user_id)
	mail = get_mail(user_id)
	plea_date = now.strftime('%Y%m%d%H%M%S')
	description = get_plea_info(user_id)

	photos = [x for x in listdir(join(path)) if isfile(join(path, x)) and len(x) != len(x.replace('.jpg', '').replace('.png', ''))]
	for photo in photos:
		filesize = stat(join(path, photo)).st_size
		try:
			rest = send_photo(join(path, photo), photo)
			if type(rest) is not str:
				fileguid = rest.text.replace('"', '')

			else:
				return rest

		except Exception as e:
			return e

		file = {
			'FileName': photo,
			'FileGUID': fileguid,
			'FileSize': filesize
		}
		files.append(file)

	request_data = {
		'RequestType': GUID_plea,
		'RequestData': plea_date,
		'InitiatorPhone': phone_number,
		'InitiatorEmail': mail,
		'Description': description,
		'Files': files
	}
	headers = {
		'Content-type': 'application/json',
	 	'Accept': 'text/plain'
	 	}
	try:
		req = requests.post(post_plea_url, json = request_data, headers = headers, auth = HTTPBasicAuth(api_login, api_password), timeout = 30)
		if req.status_code == 200:
			return 'Успешно'

		else:
			return req.text

	except Exception as e:
		return e
		


