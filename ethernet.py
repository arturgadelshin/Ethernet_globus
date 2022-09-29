import logging
import socket
#import parser_ethernet
#import send
#import receive

from GUI.gui import*
from base_interface_function import*
from send import len_command
from parsing_ethernet import*
import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QLabel
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QStatusBar
from PyQt5.QtWidgets import QToolBar
from PyQt5.QtWidgets import QWidget, QDesktopWidget, QApplication


#app = QtWidgets.QApplication(sys.argv)

#win = QtWidgets.QWidget()
#win = Window()


#qr = win.frameGeometry()
#cp = QDesktopWidget().availableGeometry().center()
#qr.moveCenter(cp)
#win.move(qr.topLeft())

#win.show()
#sys.exit(app.exec_())

class Ethernet:
    """ Класс для работы с ethernet, настройка абоненета, прием-передача """
    client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # Установка типа сети UPD

    def __init__(self, host_,port_):
        self.host = host_
        self.port = port_

    def swap(self, command):
        uid = None # Разобраться с UID
        len_com = len_command(command)
        com = command
        msg = uid+len_com+com
        self.client.sendto(bytes(msg),(self.host,self.port))
        data = self.client.recvfrom(512)
        self.client.close()
        return data


# client = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# id= [0,26]
#
# #uid = struct.pack("<H", id)
# com = replace_ip('192.168.1.20')
# #com = read_testinfo_and_rgsmk(1)
# #msg = reset_em(0)
# len_com = len_command(com)
#
# msg = id+len_com+com
# client.sendto(bytes(msg), (host, port))
# print(bytes(msg))
#
#
#
#
#
#
# #print(msg.encode('utf-8'))
#
#
#
# d = client.recvfrom(1024)
# logging.debug(d[0])
#
# reply = d[0]
# addr = d[1]
# rec = Parsing()
#
# rec.info_parsing_packet(d[0])
#
# print(addr)
#
# client.close()
#

