from uiwindow import *

from datetime import date
from PyQt5 import QtWidgets
import xml.etree.ElementTree as ET
import sys
import hashlib
import requests
import csv


class UpLoad:
    def upload(self):  # main func
        if self.filename != None:
            self.login = ui.lineEdit_login.text()
            password = ui.lineEdit_password.text()
            self.sha1pass = hashlib.sha1(password.encode('utf-8')).hexdigest()
            self.address = ui.lineEdit_adress.text()
            self.port = ui.lineEdit_port.text()
            self.protocol = ui.protocol.currentText()
            self.bd = '/resto'
            self.auth()
            self.get_store()  # первый склад в списке
            current_date = date.today()
            day = current_date.strftime("%d.%m.%Y")
            data = """<document>
              <items>\n"""
            data += self.pars()
            data += """  </items>
              <status>NEW</status>
              <accountToCode>5.01</accountToCode>
              <revenueAccountCode>4.01</revenueAccountCode>
              <documentNumber>%s</documentNumber>
              <dateIncoming>%s</dateIncoming>
            </document>""" % (self.filename.split("/")[-1], day)
            self.up(data)
            ui.resulttext.setText("Успешно")
            self.logout()
        else:
            ui.filenametext.setText("Заполните все поля")

    def auth(self):
        auth_url = (self.protocol + '://' + self.address + ':' + self.port + self.bd + '/api/auth?login=' +
                    self.login + '&pass=' + self.sha1pass)
        self.token = requests.get(auth_url)
        ui.progressBar.setProperty("value", 17)

    def get_store(self):
        gets_url = (self.protocol + '://' + self.address + ':' + self.port + self.bd + '/api/corporation/stores?key=' +
                    self.token.text)
        stores = requests.get(gets_url)  # store получить guid
        root = ET.fromstring(stores.content)
        self.store = root[0][0].text
        ui.progressBar.setProperty("value", 34)

    def get_product(self, name):
        getp_url = (self.protocol + '://' + self.address + ':' + self.port + self.bd + '/api/products/search?key=' +
                    self.token.text + '&name=' + name)
        product = requests.get(getp_url)  # спарсить product, чтобы получить guid
        root = ET.fromstring(product.content)
        ty = root.find('productDto')
        if ty is None:
            return None
        else:
            return root[0][0].text
    
    # Logout, отпускаем лицензию
    def logout(self):
        out_url = (self.protocol + '://' + self.address + ':' + self.port + self.bd + '/api/logout?key=' +
                   self.token.text)
        requests.get(out_url)
        print("Документ загружен успешно.")
        ui.progressBar.setProperty("value", 100)

    # Выбор файла, получение имени файла
    def choose_file(self):
        self.filename = QtWidgets.QFileDialog.getOpenFileName(None, "Open File", "", "All Files (*.csv)")[0]
        print(self.filename)
        ui.filenametext.setText(self.filename.split("/")[-1])

    def convert_row(self, row):
        return """\t  <item>
                      <discountSum>0</discountSum>
                      <sum>%s</sum>
                      <amount>%s</amount>
                      <productId>%s</productId>
                      <productArticle>0</productArticle>
                      <storeId>%s</storeId> 
              </item>\n""" % (row[2], row[1], row[0], self.store)

    def pars(self):
        f = open(self.filename, encoding='utf-8')
        csv_f = csv.reader(f, delimiter=";")
        data = ""
        count = 0
        for row in csv_f:
            if count == 0:
                count += 1
                continue
            id = self.get_product(row[1])
            if id is None:
                continue
            data += self.convert_row([id, row[3], row[6]])
        f.close()
        return data

    def up(self, xml):
        post_url = (self.protocol + '://' + self.address + ':' + self.port + self.bd +
                    '/api/documents/import/salesDocument?key=' + self.token.text)
        headers = {'Content-Type': 'application/xml'}  # set what your server accepts
        requests.post(post_url, data=xml, headers=headers)
        ui.progressBar.setProperty("value", 68)


app = QtWidgets.QApplication(sys.argv)
Form = QtWidgets.QWidget()
app.setStyle('Fusion')
up = UpLoad()
ui = Ui_Form()
ui.setupUi(Form)
Form.show()
ui.choosefile.clicked.connect(up.choose_file)
ui.upload.clicked.connect(up.upload)
sys.exit(app.exec_())
