import requests
import hashlib
import os
import csv
import xml.etree.ElementTree as ET

success = '<Response [200]>'
fail = '<Response [400]>'


# Проверка на наличие файла
def check_file(filename):
    if os.path.exists(filename) and os.path.isfile(filename):
        print('Загрузка файла ' + filename + ' началась.')
        print('Размер:', os.path.getsize(filename), 'Байт.')
        return True
    else:
        print('Не удалось обнаружить файл ' + filename + ' проверьте корректность ввода.')
        return False
        #try-except
        #rest api


def pars(filename):
    f = open(filename, encoding='utf-8')
    csv_f = csv.reader(f, delimiter=";")
    data = ""
    count = 0
    for row in csv_f:
        if count == 0:
            count += 1
            continue
        id = get_product(row[1])
        if id is None:
            continue
        data += convert_row([id, row[3], row[6]])
    f.close()
    return data


def convert_row(row):
    return """\t  <item>
                  <discountSum>0</discountSum>
                  <sum>%s</sum>
                  <amount>%s</amount>
                  <productId>%s</productId>
                  <productArticle>0</productArticle>
                  <storeId>%s</storeId> 
          </item>\n""" % (row[2], row[1], row[0], store_id)


def get_store():
    gets_url = (protocol + '://' + server + ':' + port + bd + '/api/corporation/stores?key=' + token.text)
    store = requests.get(gets_url)  # спарсить store, чтобы получить guid
    root = ET.fromstring(store.content)
    return root[0][0].text


def get_product(name):
    getp_url = (protocol + '://' + server + ':' + port + bd + '/api/products/search?key=' + token.text + '&name='
                + name)
    product = requests.get(getp_url)  # спарсить product, чтобы получить guid
    root = ET.fromstring(product.content)
    ty = root.find('productDto')
    if ty is None:
        return None
    else:
        return root[0][0].text


# Хеширование пароля в sha1/отправка запроса на получение токена
def auth():
    sha1pass = hashlib.sha1(password.encode('utf-8')).hexdigest()
    auth_url = (protocol + '://' + server + ':' + port + bd + '/api/auth?login=' + login + '&pass=' + sha1pass)
    token = requests.get(auth_url)
    return token


# Формирование и отправка запроса на выгрузку xml
def upload(token, xml):
    post_url = (protocol + '://' + server + ':' + port + bd + '/api/documents/import/salesDocument?key=' + token.text)
    headers = {'Content-Type': 'application/xml'}  # set what your server accepts
    answer = str(requests.post(post_url, data=xml, headers=headers))
    result(answer)


# Logout, отпускаем лицензию
def logout(token):
    out_url = (protocol + '://' + server + ':' + port + bd + '/api/logout?key=' + token.text)
    requests.get(out_url)


# Результат
def result(answer):
    if answer == success:
        print('Загрузка файла ' + filename + ' прошла успешно.')
    else:
        print('Загрузка файла ' + filename + ' не выполнена, обратитесь к администратору.' + '\n' + 'Код ошибки' +
              answer)


# Авторизация и выбор сервера (перенести на GUI)
login = input("Введите логин: ")
password = input("Введите пароль: ")
protocol = input("Введите протокол безопасности (http/https): ")
server = input("Введите адрес сервера: ")
port = input("Введите порт: ")
bd = '/resto'
file_flag = False
while not file_flag:
    filename = input("Введите название загружаемого файла: ")
    file_flag = check_file(filename)
token = auth()
store_id = get_store()
data = """<document>
  <items>\n"""
data += pars(filename)
data += """  </items>
  <status>NEW</status>
  <accountToCode>5.01</accountToCode>
  <revenueAccountCode>4.01</revenueAccountCode>
  <documentNumber>%s</documentNumber>
  <dateIncoming>19.09.2022</dateIncoming>
</document>""" % (filename)
print(data)
upload(token, data)
logout(token)
