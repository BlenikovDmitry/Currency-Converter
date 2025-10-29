import requests
from datetime import *
import xmltodict
import json
import time


'''
Тянем данные с сайта ЦБ
Есть нюанс: так как данные отдаются в формате xml, их преобразуем в формат списка питон, после уже парсим json
'''
def get_data():
    date_str = datetime.now().strftime('%d/%m/%Y')
    url = f"https://www.cbr.ru/scripts/XML_daily.asp?date_req={date_str}"
    resp = requests.get(url)
    python_dict = xmltodict.parse(resp.text)
    json_string = json.dumps(python_dict, indent=4, ensure_ascii=False)
    python_obj = json.loads(json_string)
    data = python_obj['ValCurs']['Valute']
    return data

'''
класс исключения
'''
class APIException(Exception):
    def __init__(self, message):
        self.message = message
'''
Класс реализующий статический метод get_price
Экономим на запросах к сайту ЦБ - считаем данные сразу, после будем использовать
'''
class Business_Logic():
    data = get_data()
    def get_price(base, quote, amount):
        curr_base = 0
        curr_quote = 0
        '''
        на сайте ЦБ РФ нет курса рубля к рублю, поэтому нужно для таких случаев
        и для случая когда валюта исходная и целевая одинаковы, прописать
        отдельную логику
        '''
        if base == '' or quote == '':
            raise APIException('Валюты не заданы')
            
        if base == 'RUB' and quote == 'RUB' or base == quote:
            raise APIException('Одинаковые валюты')
        if base == 'RUB':
            curr_base = 1
            for i in Business_Logic.data:
                if i['CharCode'] == quote:
                    curr_quote =  float(i['VunitRate'].replace(',', '.'))
                    result = (curr_base / curr_quote) * int(amount)
                    return result
        if quote == 'RUB':
            curr_quote = 1
            for i in Business_Logic.data:
                if i['CharCode'] == quote:
                    curr_base =  float(i['VunitRate'].replace(',', '.'))
                    result = (curr_base / curr_quote) * int(amount)
                    return result
            
                
        '''
        бежим по данным, когда находим исходную валюту и валюту назначения
        запоминаем их курс, считаем и возвращаем с основную программу
        '''
        for i in Business_Logic.data:
            if i['CharCode'] == base:
                curr_base = float(i['VunitRate'].replace(',', '.'))
            if i['CharCode'] == quote:
                curr_quote =  float(i['VunitRate'].replace(',', '.'))
        if curr_base == 0:
            raise APIException(f'валюта {base} не существует')
        if curr_quote == 0:
            raise APIException(f'валюта {quote} не существует')
        if not str(amount).isdigit() or not float(amount).is_integer():
            raise APIException('количество валюты должно быть целое число')
        result = (curr_base / curr_quote) * int(amount)
        return round(result,2)

    
    def __init__(self):
        pass

   
    
'''
Функция парсит строку ввода без команд чтобы выдрать валюты и количество для конвертации
'''
def parse(message):
    '''
отлавливаем ошибку когда данные введены не полностью
2 кода валюты + 2 пробела + 1 цифра == 9
если строка < символов и это не команда - то это ошибка 
    '''
    if len(message) < 9:
        BASE = ''
        QUOTE = ''
        AMOUNT = ''
        return BASE, QUOTE, AMOUNT
    
    pos = message.find(' ')
    BASE = message[0:pos]
    message = message[pos+1:]
    pos = message.find(' ')
    QUOTE = message[0:pos]
    message = message[pos+1:]
    AMOUNT = message[0:]
    return BASE, QUOTE, AMOUNT
