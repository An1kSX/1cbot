# -*- coding: UTF-8 -*-
from pyrogram import filters
from bot_settings import bot
from languages import languages
from pyrogram.types import KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from db_functions import new_user, state_change, state_get, authorize_user, is_authorized
from db_functions import increase_plea_num, get_plea_num
from db_functions import set_phone_number, set_mail, clear_number
from db_functions import set_plea_type, set_plea_info, clear_plea_type_and_info
from api_request import send_plea_to_1c, get_plea_types, get_mails
from os import mkdir, listdir
from os.path import abspath, dirname, join
from datetime import datetime as date
from shutil import rmtree
from re import search, match






language = 'ru'



@bot.on_message(filters.contact & filters.incoming & filters.private) 
def contact_handler(_, message):
	new_user(message.chat.id)
	state = state_get(message.chat.id)

	if state == 'send_phone_number':
		phone_number = search(r'(33|93|99|94|97|90|95|91|98|88).*\d{3}.*\d{2}.*\d{2}', message.contact.phone_number)
		if phone_number is None:
			bot.send_message(
				chat_id = message.chat.id,
				text = languages[language]['incorrect_number']
				)
			return 

		set_phone_number(message.chat.id, message.contact.phone_number)
		bot.send_message(
			chat_id = message.chat.id,
			text = languages[language]['number_added'],
			reply_markup = ReplyKeyboardMarkup([[KeyboardButton(languages[language]['complete_plea'])], [KeyboardButton(languages[language]['back'])], [KeyboardButton(languages[language]['cancel_filling'])]], resize_keyboard = True)
			)
		state_change(message.chat.id, 'number_added')





@bot.on_message(filters.command('start') & filters.private & filters.incoming)
def start(_, message):
	new_user(message.chat.id)
	state = state_get(message.chat.id)

	if is_authorized(message.chat.id) != 1:                                   
		bot.send_message(
			chat_id = message.chat.id,
			text = languages[language]['send_mail'],
			reply_markup = ReplyKeyboardRemove()
			)
		state_change(message.chat.id, 'set_mail')
		return

	try:
		if state != 'menu':
			plea_num = get_plea_num(message.chat.id)
			rmtree(f'{message.chat.id}_{plea_num}')
	except:
		pass


	bot.send_message(
		chat_id = message.chat.id,
		text = languages[language]['welcome'],
		reply_markup = ReplyKeyboardMarkup([[KeyboardButton(languages[language]['add_photo'])], [KeyboardButton(languages[language]['change_email'])]], resize_keyboard = True)
		)
	state_change(message.chat.id, 'menu')
	clear_number(message.chat.id)
	clear_plea_type_and_info(message.chat.id)




@bot.on_message(filters.text & filters.private & filters.incoming)
def text_handler(_, message):
	new_user(message.chat.id)
	state = state_get(message.chat.id)
	plea_num = get_plea_num(message.chat.id)
	if is_authorized(message.chat.id) != 1 and state != 'set_mail':
		bot.send_message(
			chat_id = message.chat.id,
			text = languages[language]['send_mail'],
			reply_markup = ReplyKeyboardRemove()
			)
		state_change(message.chat.id, 'set_mail')
		return


	if (message.text == languages[language]['add_photo']) and (state == 'menu'):
		try: 
			mkdir(f'{message.chat.id}_{plea_num}')

		except:
			try:
				rmtree(f'{message.chat.id}_{plea_num}')
				mkdir(f'{message.chat.id}_{plea_num}')

			except Exception as e:
				bot.send_message(
					chat_id = message.chat.id,
					text = e
					)
				return

		bot.send_message(
			chat_id = message.chat.id,
			text = languages[language]['send_photo'],
			reply_markup = ReplyKeyboardMarkup([[KeyboardButton(languages[language]['without_photo'])] ,[KeyboardButton(languages[language]['cancel_filling'])]], resize_keyboard = True)
			)

		state_change(message.chat.id, 'add_photo')


	elif (message.text == languages[language]['without_photo']) and (state == 'add_photo'):
		message.text = languages[language]['fill_info']
		state_change(message.chat.id, 'photo_added')
		text_handler(_, message)


	elif (message.text == languages[language]['change_email']) and (state == 'menu'):
		bot.send_message(
			chat_id = message.chat.id,
			text = languages[language]['new_email'],
			reply_markup = ReplyKeyboardMarkup([[KeyboardButton(languages[language]['cancel'])]], resize_keyboard = True)
			)
		state_change(message.chat.id, 'change_email')


	elif (message.text == languages[language]['cancel']) and (state == 'change_email'):
		state_change(message.chat.id, 'menu')
		start(_, message)


	elif (state == 'change_email') and (message.text != languages[language]['cancel']):
		try:
			mails = get_mails()
			mails = mails.json()

		except:
			bot.send_message(
				chat_id = message.chat.id,
				text = languages[language]['error_request']
				)
			bot.send_message(
				chat_id = message.chat.id,
				text = mails
				)
			return

		try:
			for mail in mails:
				if len(message.text.replace(mail['Description'], '')) != len(message.text):
					bot.send_message(
						chat_id = message.chat.id,
						text = languages[language]['email_changed']
						)
					set_mail(message.chat.id, message.text)
					state_change(message.chat.id, 'menu')
					start(_, message)
					return

		except:
			pass

		bot.send_message(
			chat_id = message.chat.id,
			text = languages[language]['incorrect_mail']
			)


	elif state == 'set_mail':
		try:
			mails = get_mails()
			mails = mails.json()

		except:
			bot.send_message(
				chat_id = message.chat.id,
				text = languages[language]['error_request']
				)
			bot.send_message(
				chat_id = message.chat.id,
				text = mails
				)
			return


		try:
			for mail in mails:
				if len(message.text.replace(mail['Description'], '')) != len(message.text):
					bot.send_message(
						chat_id = message.chat.id,
						text = languages[language]['successful_authorization']
						)
					set_mail(message.chat.id, message.text)
					state_change(message.chat.id, 'menu')
					authorize_user(message.chat.id)
					start(_, message)
					return

		except:
			pass

		bot.send_message(
			chat_id = message.chat.id,
			text = languages[language]['incorrect_mail']
			)


	elif (message.text == languages[language]['add_more_photo']) and (state == 'photo_added'):
		path = dirname(abspath(__file__))
		if len([x for x in listdir(join(path, f'{message.chat.id}_{plea_num}')) if len(x.replace('jpg', '').replace('png', '')) != len(x)]) >= 5:
			bot.send_message(
				chat_id = message.chat.id,
				text = languages[language]['photo_max']
				)
			return

		bot.send_message(
			chat_id = message.chat.id,
			text = languages[language]['send_more_photo'],
			reply_markup = ReplyKeyboardMarkup([[KeyboardButton(languages[language]['cancel'])]], resize_keyboard = True)
			)
		state_change(message.chat.id, 'add_photo')


	elif message.text == languages[language]['cancel_filling']:
		bot.send_message(
			chat_id = message.chat.id,
			text = languages[language]['come_back_main_menu'],
			reply_markup =  ReplyKeyboardMarkup([[KeyboardButton(languages[language]['add_photo'])], [KeyboardButton(languages[language]['change_email'])]], resize_keyboard = True)
			)
		state_change(message.chat.id, 'menu')
		clear_number(message.chat.id)
		clear_plea_type_and_info(message.chat.id)
		path = dirname(abspath(__file__))
		[rmtree(join(path, x)) for x in listdir(join(path)) if len(x.replace(str(message.chat.id), '')) != len(x)]


	elif (message.text == languages[language]['cancel']) and (state == 'add_photo'):
		path = dirname(abspath(__file__))
		if len([x for x in listdir(join(path, f'{message.chat.id}_{plea_num}')) if len(x.replace('jpg', '').replace('png', '')) != len(x)]) < 5:
			bot.send_message(
				chat_id = message.chat.id,
				text = languages[language]['come_back'],
				reply_markup = ReplyKeyboardMarkup([[KeyboardButton(languages[language]['fill_info'])], [KeyboardButton(languages[language]['add_more_photo'])], [KeyboardButton(languages[language]['cancel_filling'])]], resize_keyboard = True)
				)
		else:
			bot.send_message(
				chat_id = message.chat.id,
				text = languages[language]['come_back'],
				reply_markup = ReplyKeyboardMarkup([[KeyboardButton(languages[language]['fill_info'])], [KeyboardButton(languages[language]['cancel_filling'])]], resize_keyboard  = True)
				)
		state_change(message.chat.id, 'photo_added')


	elif (message.text == languages[language]['fill_info']) and (state == 'photo_added'):
		try:
			types = get_plea_types()
			types = types.json()

		except:
			bot.send_message(
				chat_id = message.chat.id,
				text = languages[language]['error_request']
				)
			bot.send_message(
				chat_id = message.chat.id,
				text = types
				)
			return

		markup = [[KeyboardButton(x['Description'])] for x in types]
		markup.append([languages[language]['back']])

		bot.send_message(
			chat_id = message.chat.id,
			text = languages[language]['choose_type'],
			reply_markup = ReplyKeyboardMarkup(markup, resize_keyboard = True)
			)
		state_change(message.chat.id, 'choose_type')


	elif state == 'choose_type':
		if message.text == languages[language]['back']:
			clear_plea_type_and_info(message.chat.id)
			path = dirname(abspath(__file__))
			if len([x for x in listdir(join(path, f'{message.chat.id}_{plea_num}')) if len(x.replace('jpg', '').replace('png', '')) != len(x)]) < 5:
				bot.send_message(
					chat_id = message.chat.id,
					text = languages[language]['come_back'],
					reply_markup = ReplyKeyboardMarkup([[KeyboardButton(languages[language]['fill_info'])], [KeyboardButton(languages[language]['add_more_photo'])], [KeyboardButton(languages[language]['cancel_filling'])]], resize_keyboard = True)
					)
			else:
				bot.send_message(
					chat_id = message.chat.id,
					text = languages[language]['photo_max'],
					reply_markup = ReplyKeyboardMarkup([[KeyboardButton(languages[language]['fill_info'])], [KeyboardButton(languages[language]['cancel_filling'])]], resize_keyboard  = True)
					)
			state_change(message.chat.id, 'photo_added')
			return

		try:
			types = get_plea_types()
			types = types.json()

		except:
			bot.send_message(
				chat_id = message.chat.id,
				text = languages[language]['error_request']
				)
			bot.send_message(
				chat_id = message.chat.id,
				text = types
				)
			return

		for x in types:
			if x['Description'] == message.text:
				set_plea_type(message.chat.id, x['GUID'])

				bot.send_message(
					chat_id = message.chat.id,
					text = languages[language]['input_info'],
					reply_markup = ReplyKeyboardMarkup([[KeyboardButton(languages[language]['back'])], [KeyboardButton(languages[language]['cancel_filling'])]], resize_keyboard = True)
					)
				state_change(message.chat.id, 'add_info')
				return

		bot.send_message(
			chat_id = message.chat.id,
			text = languages[language]['incorrect_type']
			)


	elif (message.text == languages[language]['back']) and (state == 'add_info'):
		try:
			types = get_plea_types()
			types = types.json()

		except:
			bot.send_message(
				chat_id = message.chat.id,
				text = languages[language]['error_request']
				)
			bot.send_message(
				chat_id = message.chat.id,
				text = types
				)
			return

		markup = [[KeyboardButton(x['Description'])] for x in types]
		markup.append([languages[language]['back']])

		bot.send_message(
			chat_id = message.chat.id,
			text = languages[language]['choose_type'],
			reply_markup = ReplyKeyboardMarkup(markup, resize_keyboard = True)
			)
		state_change(message.chat.id, 'choose_type')

	elif state == 'add_info':
		if (len(message.text) > 2048):
			bot.send_message(
				chat_id = message.chat.id,
				text = languages[language]['long_text']
				)
			return

		set_plea_info(message.chat.id, message.text)
		bot.send_message(
			chat_id = message.chat.id,
			text = languages[language]['info_filled'],
			reply_markup = ReplyKeyboardMarkup([[KeyboardButton(languages[language]['create_plea'])], [KeyboardButton(languages[language]['change_text'])], [KeyboardButton(languages[language]['cancel_filling'])]], resize_keyboard = True)
			)
		state_change(message.chat.id, 'info_added')


	elif (message.text == languages[language]['change_text']) and (state == 'info_added'):
		bot.send_message(
			chat_id = message.chat.id,
			text = languages[language]['input_info'],
			reply_markup = ReplyKeyboardMarkup([[KeyboardButton(languages[language]['back'])], [KeyboardButton(languages[language]['cancel_filling'])]], resize_keyboard = True)
			)
		state_change(message.chat.id, 'add_info')


	elif (message.text == languages[language]['create_plea']) and (state == 'info_added'):
		bot.send_message(
			chat_id = message.chat.id,
			text = f'{languages[language]["send_phone_number"]}',
			reply_markup = ReplyKeyboardMarkup([[KeyboardButton(languages[language]['send_number'], request_contact = True)], [KeyboardButton(languages[language]['back'])], [KeyboardButton(languages[language]['cancel_filling'])]], resize_keyboard = True)
			) 
		state_change(message.chat.id, 'send_phone_number')

	elif (message.text == languages[language]['back']) and (state == 'send_phone_number'):
		clear_number(message.chat.id)
		bot.send_message(
			chat_id = message.chat.id,
			text = languages[language]['come_back'],
			reply_markup = ReplyKeyboardMarkup([[KeyboardButton(languages[language]['create_plea'])], [KeyboardButton(languages[language]['change_text'])], [KeyboardButton(languages[language]['cancel_filling'])]], resize_keyboard = True)
			)
		state_change(message.chat.id, 'info_added')

	elif (message.text != languages[language]['back']) and (state == 'send_phone_number'):
		phone_number = search(r'(33|93|99|94|97|90|95|91|98|88).*\d{3}.*\d{2}.*\d{2}', message.text)
		if phone_number is None:
			bot.send_message(
				chat_id = message.chat.id,
				text = languages[language]['incorrect_number']
				)
			return
		set_phone_number(message.chat.id, phone_number.group())
		
		bot.send_message(
			chat_id = message.chat.id,
			text = languages[language]['number_added'],
			reply_markup = ReplyKeyboardMarkup([[KeyboardButton(languages[language]['complete_plea'])], [KeyboardButton(languages[language]['back'])], [KeyboardButton(languages[language]['cancel_filling'])]], resize_keyboard = True)
			)
		state_change(message.chat.id, 'number_added')

	elif (message.text == languages[language]['back']) and (state == 'number_added'):
		bot.send_message(
			chat_id = message.chat.id,
			text = f"{languages[language]['come_back']}\n\n{languages[language]['send_phone_number']}",
			reply_markup = ReplyKeyboardMarkup([[KeyboardButton(languages[language]['send_number'], request_contact = True)], [KeyboardButton(languages[language]['back'])], [KeyboardButton(languages[language]['cancel_filling'])]], resize_keyboard = True)
			)
		state_change(message.chat.id, 'send_phone_number')

	elif (message.text == languages[language]['complete_plea']) and (state == 'number_added'):
		req = send_plea_to_1c(message.chat.id, plea_num)
		if req == 'Успешно':
			bot.send_message(
				chat_id = message.chat.id,
				text = f'{languages[language]["plea_created"]} {plea_num}',
				reply_markup = ReplyKeyboardMarkup([[KeyboardButton(languages[language]['add_photo'])], [KeyboardButton(languages[language]['change_email'])]], resize_keyboard = True)
				)
			rmtree(f'{message.chat.id}_{plea_num}')
			clear_number(message.chat.id)
			clear_plea_type_and_info(message.chat.id)
			increase_plea_num(message.chat.id)
			state_change(message.chat.id, 'menu')

		else:
			bot.send_message(
				chat_id = message.chat.id,
				text = languages[language]['error_request']
				)
			bot.send_message(
				chat_id = message.chat.id,
				text = req
				)



	elif (message.text == languages[language]['back']) and (state == 'mail_added'):
		bot.send_message(
			chat_id = message.chat.id,
			text = f"{languages[language]['come_back']}\n\n{languages[language]['send_mail']}",
			reply_markup = ReplyKeyboardMarkup([[KeyboardButton(languages[language]['back'])], [KeyboardButton(languages[language]['cancel_filling'])]], resize_keyboard = True) 
			)
		state_change(message.chat.id, 'set_mail')










@bot.on_message((filters.document | filters.photo) & filters.private & filters.incoming)
def photo_handler(_, message):
	state = state_get(message.from_user.id)
	plea_num = get_plea_num(message.from_user.id)


	if state == 'add_photo':
		try:
			if message.document.mime_type not in ['image/png', 'image/jpeg']:
				bot.send_message(
					chat_id = message.chat.id,
					text = languages[language]['photo_format']
					)
				return
		except:
			pass 

		try:
			file_name = message.document.file_name
		except:
			file_name = f'photo_{date.now().strftime("%Y-%m-%d_%H-%M-%S")}.jpg'
		bot.download_media(
			message = message,
			file_name = f'{message.from_user.id}_{plea_num}/{file_name}'
			)

		path = dirname(abspath(__file__))
		if len([x for x in listdir(join(path, f'{message.chat.id}_{plea_num}')) if len(x.replace('jpg', '').replace('png', '')) != len(x)]) < 5:
			bot.send_message(
				chat_id = message.chat.id,
				text = languages[language]['photo_added'],
				reply_markup = ReplyKeyboardMarkup([[KeyboardButton(languages[language]['fill_info'])], [KeyboardButton(languages[language]['add_more_photo'])], [KeyboardButton(languages[language]['cancel_filling'])]], resize_keyboard = True)
				)
		else:
			bot.send_message(
				chat_id = message.chat.id,
				text = languages[language]['photo_max'],
				reply_markup = ReplyKeyboardMarkup([[KeyboardButton(languages[language]['fill_info'])], [KeyboardButton(languages[language]['cancel_filling'])]], resize_keyboard  = True)
				)
		state_change(message.from_user.id, 'photo_added')







bot.run()
	


