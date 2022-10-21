from PyQt5.Qt import *
from PyQt5 import QtWidgets, QtGui, QtCore
from stages import *
#from GUI.central_window import *
from com_voltage_regulator import *
from globus_ethernet import *


class GwINSTEKWindow(QtWidgets.QDialog):
    flag_setting = 0

    def __init__(self, parent=None):
        super().__init__(parent)
        #self.resize(300, 300)

        self.layout = QGridLayout()  # Создание сетки - Основная
        # Блок первый
        self.oneblock = QtWidgets.QVBoxLayout()  # Создаем вертикальный контейнер 1
        self.combo_box_1 = QComboBox()
        self.combo_box_1.setToolTip('Задается адрес регулятора на порте')
        self.combo_box_1.setToolTipDuration(3000)
        self.combo_box_1.setFont(QtGui.QFont("Times", 10))
        self.combo_box_2 = QComboBox()
        self.combo_box_2.setToolTip('Задается скорость регулятора на порте')
        self.combo_box_2.setToolTipDuration(3000)
        self.combo_box_2.setFont(QtGui.QFont("Times", 10))
        self.combo_box_3 = QComboBox()
        self.combo_box_3.setToolTip('Установить канал через который запитан ЭМ1')
        self.combo_box_3.setToolTipDuration(3000)
        self.combo_box_3.setFont(QtGui.QFont("Times", 10))
        self.voltage_em = QtWidgets.QLineEdit()
        self.voltage_em.setFixedWidth(115)
        self.combo_box_4 = QComboBox()
        self.combo_box_4.setToolTip('Установить калибровочный канал')
        self.combo_box_4.setToolTipDuration(3000)
        self.combo_box_4.setFont(QtGui.QFont("Times", 10))

        for port in serial_ports():
            self.combo_box_1.addItem(port)
            self.combo_box_1.setInsertPolicy(0)
        self.speeds = VoltageRegulator().speeds
        for speed in self.speeds:
            self.combo_box_2.addItem(speed)
            self.combo_box_2.setCurrentText('9600')
            self.combo_box_2.setInsertPolicy(0)

        self.combo_box_3.addItem('1')
        self.combo_box_3.setInsertPolicy(0)
        self.combo_box_3.setCurrentText('1')
        self.voltage_em.setText('27')
        self.combo_box_4.addItem('2')
        self.combo_box_4.setInsertPolicy(0)
        self.combo_box_4.setCurrentText('2')


        self.button_write_settings = QtWidgets.QPushButton("Установить настройки")
        self.button_write_settings.setFont(QtGui.QFont("Times", 10))
        self.button_write_settings.setFixedWidth(150)
        # Формирование интерфейса второго блока
        self.oneblock.addWidget(self.combo_box_1, Qt.AlignCenter)
        self.oneblock.addWidget(self.combo_box_2, Qt.AlignCenter)
        self.oneblock.addWidget(self.combo_box_3, Qt.AlignCenter)
        self.oneblock.addWidget(self.voltage_em, Qt.AlignCenter)
        self.oneblock.addWidget(self.combo_box_4, Qt.AlignCenter)
        self.oneblock.addWidget(self.button_write_settings, Qt.AlignCenter)
        self.button_write_settings.clicked.connect(self.set_com_port)
        self.layout.addLayout(self.oneblock, 1, 0)
        self.setLayout(self.layout)
        GwINSTEKWindow.flag_setting = 1

    def set_com_port(self):
        port = self.combo_box_1.currentText()
        speed = self.combo_box_2.currentText()
        voltage_em = self.voltage_em.text()
        channel_em = self.combo_box_3.currentText()
        channel_calibrate = self.combo_box_4.currentText()
        VoltageRegulator.port = port
        VoltageRegulator.speed = speed
        VoltageRegulator.voltage_em = voltage_em
        VoltageRegulator.channel_em = channel_em
        VoltageRegulator.channel_calibrate = channel_calibrate
        self.close()
