from GUI.calibrate import *
import sys  # sys нужен для передачи argv в QApplication
from PyQt5 import QtWidgets
from GUI.mdi_window import *
global win


def main():
    app = QtWidgets.QApplication(sys.argv)  # Новый экземпляр QApplication

    win = MDIWindow()  # Создаём объект класса ExampleApp
    #win = CentralWindow()  # Создаём объект класса ExampleApp

    win.resize(900, 400)
    win.setWindowTitle('Ethernet')
    win.show()  # Показываем окно
    app.exec_()  # и запускаем приложение
    #sys.exit(app.exec_())


if __name__ =='__main__':
    main()
