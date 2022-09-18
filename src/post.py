import requests
import hashlib
import os


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


# Хеширование пароля в sha1/отправка запроса на получение токена
def auth():
    sha1pass = hashlib.sha1(password.encode('utf-8')).hexdigest()
    auth_url = (protocol + '://' + server + ':' + port + bd + '/api/auth?login=' + login + '&pass=' + sha1pass)
    token = requests.get(auth_url)
    return token


# Формирование и отправка запроса на выгрузку xml
def upload(token):
    post_url = (protocol + '://' + server + ':' + port + bd + '/api/documents/import/salesDocument?key=' + token.text)
    xml = open(filename, 'rb').read().decode('utf-8')
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
upload(token)
logout(token)
