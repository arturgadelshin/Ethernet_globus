from PyQt5.QtWidgets import QMessageBox

from GUI.calibrate import *
from GUI.central_window import *


class MDIWindow(QMainWindow): # Использовать для основного окна

    """Main Window."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        #self.setCentralWidget(CentralWindow()) # Вызов в центральный виджет своего виджета
        self.mdi = QMdiArea()
        self.setCentralWidget(self.mdi)

        self.createMenu()
        #self._createToolBar()
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def createMenu(self):
        self.menu_1 = self.menuBar().addMenu("&Меню")
        self.menu_1.addAction('&Проверка по ТУ', self.prov_tu)
        self.menu_1.addAction('&Ручная калибровка', self.calibrate_channel)
        self.menu_1.addAction('&Автоматическая калибровка', self.calibrate_automatic_channel)
        self.menu_1.addAction('&О программе', self.about)
        self.menu_1.addAction('&Выход', self.close)
        self.menu_2 = self.menuBar().addMenu("&Вид")
        self.menu_2.addAction('&Каскад', self.window_cascade)
        self.menu_2.addAction('&Плитка', self.window_tiled)

    def about(self):
        msg_box = QMessageBox( 1,
                              "О программе",
                              "Программа изначально задумывалась для проверки и сдачи по ТУ - ЭМ1 6П675Н."
                              " В программе заложена реализация поканальной и автоматической калибровки ЭМ1."
                              " Планируется реализовать полностью автоматическую проверку и передать ЭМ1 в цех. \n"
                              "\n"
                              " Дата начала разработки: 01.07.22 \n"
                              " Разработчик: Гадельшин А.Р.\n"
                              " Сайт: https://www.arturgadelshin.ru\n"
                              " GitHub: https://github.com/arturgadelshin\n"
                              " Телефон: 24-21 \n",
                              buttons=QtWidgets.QMessageBox.Ok,
                              parent=None
                              )
        msg_box.exec_()

    def window_cascade(self):
        self.mdi.cascadeSubWindows()

    def window_tiled(self):
        self.mdi.tileSubWindows()

    def prov_tu(self):
        #MDIWindow.count = MDIWindow.count + 1
        sub = QMdiSubWindow()
        sub.setWidget(CentralWindow(self.mdi))
        self.mdi.addSubWindow(sub)
        sub.show()

    def calibrate_channel(self):
        sub = QMdiSubWindow()
        sub.resize(900,300)
        #sub.minimumSize(600,300)
        sub.setWidget(CalibrateWindow(self.mdi))
        self.mdi.addSubWindow(sub)
        sub.show()

    def calibrate_automatic_channel(self):
        sub = QMdiSubWindow()
        sub.setMinimumSize(600, 200)
        sub.setWidget(CalibrateAutomaticWindow(self.mdi))
        self.mdi.addSubWindow(sub)
        sub.show()

    def _createToolBar(self):
        tools = QToolBar()
        self.addToolBar(tools)
        tools.addAction('Настройка', self.close)
        tools.addAction('Выход', self.close)

    def _createStatusBar(self, text):
        print(text)
        self.statusBar.showMessage(text, 1)

    def _clearMessage(self):
        print('ggg')
        #self.status.clearMessage()
        #self._createStatusBar.clearMessage()

    def set_voltage_regulator(self):
        sub = QMdiSubWindow()
        sub.setMinimumSize(200, 200)
        sub.setWindowTitle('COM порт')
        sub.setWidget(SetVoltageRegulatorWindow(self.mdi))
        self.mdi.addSubWindow(sub)
        sub.show()
