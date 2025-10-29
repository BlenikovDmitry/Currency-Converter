import telebot
from telebot import types
import config as cnf
import extensions as ext


#из конфига подтягиваем валюты для вывода командой /values
MAIN_VALUTES = cnf.MAIN_VALUTES


bot = telebot.TeleBot(cnf.bot_token);
'''
основной слушатель сообщений
принимает команды или строку ввода пользователя на конвертацию
'''
@bot.message_handler(content_types=['text'])
def get_text_messages(message):
    if message.text[0:6] == "/start":
        start_message(message)
    elif message.text[0:5] == "/help":
        help_message(message)

        
    elif message.text == "/values":
        print_all_values(message)
    else:
        '''
        отлавливаем ошибки классом исключения
        внутри отлова парсим строку ввода, передаем ее статическому методу get_price() - размещен в классе Business_Logic в файле extensions.py
        и выводим результат или текст ошибки(если что - то пошло не так)
        '''
        try:
            BASE, QUOTE, AMOUNT = ext.parse(message.text)
            bot.send_message(message.chat.id, f"Конвертируем...")
            result = ext.Business_Logic.get_price(BASE.upper(), QUOTE.upper(), AMOUNT)
            bot.send_message(message.chat.id, f"Вам нужно  {round(result,2)} {QUOTE}")
        except ext.APIException as e:
            bot.send_message(message.chat.id, f"Ошибка: {e}")
            help_message(message)
        

    
    
'''
функция вызывается при команде /start
'''
def start_message(message):
    bot.send_message(message.chat.id,"Привет, друг! Здесь ты можешь следующее:")
    bot.send_message(message.chat.id,"<валюта в наличии(код)> <нужная валюта(код)><количество> - сконвертирует как надо")
    bot.send_message(message.chat.id,"например: eur usd 100")
    bot.send_message(message.chat.id,"/values выведет все курсы, которые я знаю")
    bot.send_message(message.chat.id,"/help получить помощь по командам")
'''
функция вызывается при команде /help
'''
def help_message(message):
    bot.send_message(message.chat.id,"Напомню о том, что можно:")
    bot.send_message(message.chat.id,"<валюта в наличии(код)><нужная валюта(код)><количество> - сконвертирует как надо")
    bot.send_message(message.chat.id,"например: eur usd 100")
    bot.send_message(message.chat.id,"/values выведет все курсы, которые я знаю")
    bot.send_message(message.chat.id,"/help получить помощь по командам")
    


'''
        выводим значения
        но есть нюанс - блочит когда много запросов.
        Если выводить с задержкой, то тратит примерно 10 минут на 55 валют, это неприемлемо
        поэтому список валют доступных к выводу командой /values есть в config.py
'''
def print_all_values(message):
    bot.send_message(message.chat.id, "Вот основные валюты, которые я знаю: ")
    bot.send_message(message.chat.id, "Вообще, я могу конвертировать " + str(len(ext.Business_Logic.data)) + ' валют но вывожу основные')
    bot.send_message(message.chat.id, "Беру данные отсюда: https://www.cbr.ru/currency_base/daily/")
    for i in ext.Business_Logic.data:
        if i['CharCode'] in MAIN_VALUTES:
            bot.send_message(message.chat.id, f'Валюта: ' + str(i['Name']))
            bot.send_message(message.chat.id, f'Код: ' + str(i['CharCode']))
            bot.send_message(message.chat.id, f'Цена за 1 единицу(в рублях): ' + str( round(float(i['VunitRate'].replace(',', '.')), 3)))






bot.polling(none_stop=True, interval=0)
    
