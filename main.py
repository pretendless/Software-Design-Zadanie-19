import telebot
import time
import os
import middleware
import models
import config
from flask import request
from datetime import datetime, timedelta
from tool import language_check, log, create_inlineKeyboard, create_markup
from app import bot, db, app, fsm
from dateutil.relativedelta import relativedelta


# ------------------ # админ панель # ------------------ #
# Обработка "старт" 
@bot.message_handler(commands=['apanel'])
@log
def apanel(message):
	text = language_check(message.from_user.id)["apanel"]
	bot.send_message(message.from_user.id, text["apanel"], reply_markup=create_inlineKeyboard({text["add_banword"]:"add_banword", text["del_banword"]:"del_banword"}))



# Добавление бан слов
@bot.callback_query_handler(func=lambda call: True and call.data.split(" ")[0] == "add_banword")
@log
def add_banword(call):
	bot.delete_message(call.from_user.id, call.message.message_id)
	text = language_check(call.from_user.id)["apanel"]
	bot.send_message(call.from_user.id, text["add_banword"], reply_markup=create_inlineKeyboard({text["back"]:"back_to_apanel"}))
	fsm.set_state(call.from_user.id, "enter_banword")


# обработка бан слова
@bot.message_handler(func=lambda message: True and fsm.get_state(message.from_user.id).state == "enter_banword")
@log
def accept_banword(message):
	text = language_check(message.from_user.id)["apanel"]
	fsm.reset_state(message.from_user.id)
	word = models.BanWords.query.filter_by(word=message.text).first()
	if word != None:
		bot.send_message(message.from_user.id, text["already"])
	else:
		db.session.add(models.BanWords(word=message.text))
		db.session.commit()
		bot.send_message(message.from_user.id, text["success"])

	bot.send_message(message.from_user.id, text["apanel"], reply_markup=create_inlineKeyboard({text["add_banword"]:"add_banword", text["del_banword"]:"del_banword"}))


# удаление бан слова
@bot.callback_query_handler(func=lambda call: True and call.data == "del_banword")
@log
def del_banword(call):
	text = language_check(call.from_user.id)["apanel"]
	words = models.BanWords.query.all()
	if len(words) == 0:
		bot.answer_callback_query(callback_query_id=call.id, text=text["empty"])
		return
	else:
		buttons = {}
		for i in words:
			buttons[i.word] = f"del_banword {i.id}"
		buttons[text["back"]] = "back_to_apanel"
		bot.send_message(call.from_user.id, text["choice_word_to_del"], reply_markup=create_inlineKeyboard(buttons))
	bot.delete_message(call.from_user.id, call.message.message_id)


# удаление бан слова
@bot.callback_query_handler(func=lambda call: True and call.data.split(" ")[0] == "del_banword")
@log
def accept_del_banword(call):
	text = language_check(call.from_user.id)["apanel"]
	word = models.BanWords.query.filter_by(id=call.data.split(" ")[1]).first()
	db.session.delete(word)
	db.session.commit()
	bot.answer_callback_query(callback_query_id=call.id, text=text["success_del"])
	bot.delete_message(call.from_user.id, call.message.message_id)
	bot.send_message(call.from_user.id, text["apanel"], reply_markup=create_inlineKeyboard({text["add_banword"]:"add_banword", text["del_banword"]:"del_banword"}))


# Обратно в админпанель
@bot.callback_query_handler(func=lambda call: True and call.data.split(" ")[0] == "back_to_apanel")
@log
def back_to_apanel(call):
	bot.delete_message(call.from_user.id, call.message.message_id)
	text = language_check(call.from_user.id)["apanel"]
	bot.send_message(call.from_user.id, text["apanel"], reply_markup=create_inlineKeyboard({text["add_banword"]:"add_banword", text["del_banword"]:"del_banword"}))



	
# ------------------ # Старт и Регистрация # ------------------ #
# Обработка "старт" 
@bot.message_handler(commands=['start'])
@log
def start(message):
	fsm.reset_state(message.from_user.id)
	text = language_check(message.from_user.id)
	if models.BotUsers.query.filter_by(user_id=str(message.from_user.id)).first() != None:
		pass
	else:
		db.session.add(models.BotUsers(user_id=str(message.from_user.id), user_name=message.from_user.username, user_firstname=message.from_user.first_name))
		db.session.commit()

	bot.send_message(message.from_user.id, text["welcome"], reply_markup=create_markup(text["menu_buttons"], 2))


# ------------------ # поиск # ------------------ # 
# ввод статей
@bot.message_handler(func=lambda message: True and message.text == language_check(message.from_user.id)["menu_buttons"][0])
@log
def enter_titles(message):
	text = language_check(message.from_user.id)["search"]
	user = models.BotUsers.query.filter_by(user_id=message.from_user.id).first()
	if user.subscribe == "Ультимейт" or user.tokens - 1 >= 0:
		bot.send_message(message.from_user.id, text["enter_titles"])
		fsm.set_state(message.from_user.id, "enter_titles")
		user.tokens -= 1
		db.session.commit()
	else:
		bot.send_message(message.from_user.id, text["wait_for_tokens"])


# обработка поиска
@bot.message_handler(func=lambda message: True and fsm.get_state(message.from_user.id).state == "enter_titles")
@log
def accept_titles(message):
	fsm.reset_state(message.from_user.id)
	text = language_check(message.from_user.id)["search"]
	tmp = bot.send_message(message.from_user.id, text["wait"])
	for i in message.text.split("\n"):
		if models.BanWords.query.filter_by(word=i).first() != None:
			bot.delete_message(message.from_user.id, tmp.message_id)
			bot.send_message(message.from_user.id, text["banword"].format(i))
			return
	try:
		path = middleware.shortest_path(message.text.split("\n")[0], message.text.split("\n")[1])
		if path == None:
			bot.delete_message(message.from_user.id, tmp.message_id)
			bot.send_message(message.from_user.id, text["no_way"])
			return

		bot.delete_message(message.from_user.id, tmp.message_id)
		bot.send_message(message.from_user.id, f"Путь: {' -> '.join(path)}\n\nДлина пути:{len(path)}")
	except Exception as e:
		print(e)
		bot.send_message(message.from_user.id, text["invalid_format"])
		fsm.reset_state(message.from_user.id)



# ------------------ # Подписка # ------------------ # 
# сообщение подписи
@bot.message_handler(func=lambda message: True and message.text == language_check(message.from_user.id)["menu_buttons"][1])
@log
def subscribe_menu(message):
	user = models.BotUsers.query.filter_by(user_id=str(message.from_user.id)).first()
	bot.send_message(message.from_user.id, language_check(message.from_user.id)["subscribe"]["template"].format(user.subscribe), reply_markup=create_inlineKeyboard({"Стандарт 100 рублей":"make_pay 100", "Ультимейт 1000 рублей":"make_pay 1000"}))



# Выставление счета
@bot.callback_query_handler(func=lambda call: True and call.data.split(" ")[0] == "make_pay")
@log
def make_pay(call):
	text = language_check(call.from_user.id)["subscribe"]
	user = models.BotUsers.query.filter_by(user_id=str(call.from_user.id)).first()
	if call.data.split(" ")[1] == "100":
		if user.subscribe in ["Стандарт", "Ультимейт"]:
			bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=text["already_subscribe"])
			return
		else:
			pass
	elif call.data.split(" ")[1] == "1000":
		if user.subscribe == "Ультимейт":
			bot.answer_callback_query(callback_query_id=call.id, show_alert=True, text=text["already_subscribe"])
			return
		else:
			pass

	bot.send_invoice(call.from_user.id,
                 title='Покупка подписки',
                 description=f'Покупка подписки',
                 invoice_payload='something_text_for_invoice',
                 provider_token=config.PAYMENT_TOKEN,
                 start_parameter='buy_product',
                 currency='rub',
                 prices=[LabeledPrice(label='Текст', amount=int(call.data.split(" ")[1])*100)])


@bot.pre_checkout_query_handler(func=lambda query: True)
def checkout(pre_checkout_query):
    bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True, 
                                  error_message="Оплата не прошла - попробуйте, пожалуйста, еще раз,"
                                                "или свяжитесь с администратором бота.")


# при корректной оплате
@bot.message_handler(content_types=['successful_payment'])
def got_payment(message):
	user = models.BotUsers.query.filter_by(user_id=str(message.from_user.id)).first()
	if int(message.successful_payment.total_amount)/100 == 100:
		subscribe = "Стандарт"
		user.tokens = 20
	else:
		subscribe = "Ультимейт"

	user.subscribe = subscribe
	db.session.commit()


"""


@app.route('/' + config.TOKEN, methods=['POST'])
def getMessage():
	bot.process_new_updates([telebot.telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
	return "!", 200


@app.route("/")
def webhook():
	bot.remove_webhook()
	bot.set_webhook(url=config.DOKKU_LINK + config.TOKEN)
	return "!", 200


# Получаем новые сообщения
if __name__ == "__main__":
	app.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000))) 
	print("START")

"""

bot.remove_webhook()
if __name__ == '__main__':
	bot.polling(none_stop=True)
	

