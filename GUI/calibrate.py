from PyQt5.Qt import *
from PyQt5 import QtWidgets, QtGui, QtCore
from stages import *
from GUI.central_window import *
from com_voltage_regulator import *
from globus_ethernet import *


class CalibrateWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout()  # Создание сетки - Основная
        self.setWindowTitle('Ручная калибровка')
        self.setFont(QtGui.QFont("Times", 10))
        # Блок первый
        self.oneblock = QtWidgets.QHBoxLayout()  # Создаем горизонтальный контейнер 1

        self.nmb_label = QtWidgets.QLabel("Номер канала")
        self.nmb_channel = QtWidgets.QLineEdit()
        self.nmb_channel.setFixedWidth(50)

        self.step_label = QtWidgets.QLabel('Шаг')
        self.step = QtWidgets.QLineEdit()
        self.step.setFixedWidth(50)

        self.vector_label = QtWidgets.QLabel('Направление калибровки')
        self.vector_calibrate = QtWidgets.QLineEdit()
        self.vector_calibrate.setFixedWidth(50)
        self.vector_calibrate.setText('1')
        self.button_write_voltage = QtWidgets.QPushButton("Установить напряжение")
        self.button_write_voltage.setFixedWidth(200)

        # Фомирование первого блока интерфейса

        self.oneblock.addWidget(self.nmb_label, Qt.AlignLeft)
        self.oneblock.addWidget(self.nmb_channel, Qt.AlignLeft)
        self.oneblock.addWidget(self.step_label, Qt.AlignLeft)
        self.oneblock.addWidget(self.step, Qt.AlignJustify)
        self.oneblock.addWidget(self.vector_label, Qt.AlignJustify)
        self.oneblock.addWidget(self.vector_calibrate, Qt.AlignJustify)
        self.oneblock.addWidget(self.button_write_voltage, Qt.AlignJustify)
        self.button_write_voltage.clicked.connect(self.set_voltage)

        self.oneblock.addStretch(100)
        self.layout.addLayout(self.oneblock, 0, 0, 1, 0)


        # Блок второй

        self.twoblock = QtWidgets.QHBoxLayout()  # Создаем горизонтальный контейнер 2
        self.dac_1_label = QtWidgets.QLabel('Значение кода ЦАП 1')
        self.dac_1 = QtWidgets.QLineEdit()
        self.dac_1.setFixedWidth(50)
        self.dac_2_label = QtWidgets.QLabel('Значение кода ЦАП 2')
        self.dac_2 = QtWidgets.QLineEdit()
        self.dac_2.setFixedWidth(50)
        self.dac_1.setText('None')
        self.dac_2.setText('None')
        self.dac_1.setReadOnly(True)
        self.dac_2.setReadOnly(True)

        # Фомирование второго блока интерфейса

        self.twoblock.addWidget(self.dac_1_label, Qt.AlignLeft)
        self.twoblock.addWidget(self.dac_1, Qt.AlignLeft)
        self.twoblock.addWidget(self.dac_2_label, Qt.AlignLeft)
        self.twoblock.addWidget(self.dac_2, Qt.AlignLeft)
        self.layout.addLayout(self.twoblock, 1, 0, 1, 0)

        # Блок третий

        self.treeblock = QtWidgets.QHBoxLayout()  # Создаем горизонтальный контейнер 2
        self.voltage_1_label = QtWidgets.QLabel('Значение напряжения ЦАП 1')
        self.voltage_1 = QtWidgets.QLineEdit()
        self.voltage_1.setFixedWidth(50)
        self.voltage_2_label = QtWidgets.QLabel('Значение напряжения ЦАП 2')
        self.voltage_2 = QtWidgets.QLineEdit()
        self.voltage_2.setFixedWidth(50)
        self.voltage_1.setText('None')
        self.voltage_2.setText('None')
        self.voltage_1.setReadOnly(True)
        self.voltage_2.setReadOnly(True)

        # Фомирование второго блока интерфейса

        self.treeblock.addWidget(self.voltage_1_label, Qt.AlignLeft)
        self.treeblock.addWidget(self.voltage_1, Qt.AlignLeft)
        self.treeblock.addWidget(self.voltage_2_label, Qt.AlignLeft)
        self.treeblock.addWidget(self.voltage_2, Qt.AlignLeft)
        self.layout.addLayout(self.treeblock, 2, 0, 1, 0)

        # Вывод содержимого сетки на экран
        self.setLayout(self.layout)


    def set_voltage(self):
        set_voltage = Calibrate()
        step = self.step.text()
        vector = self.vector_calibrate.text()
        channel = self.nmb_channel.text()
        if channel != '' and step !='':
            data = set_voltage.write_voltage_for_calibrate(step, vector, channel)
            self.dac_1.setText(hex(data[0]))
            self.dac_2.setText(hex(data[1]))
            self.voltage_1.setText(data[2])
            self.voltage_2.setText(data[3])
        else:
            msg_box = QMessageBox(QtWidgets.QMessageBox.Warning,
                                  "Внимание!",
                                  "Пожалуйста заполните поля 'Номера канала' и 'Шаг'",
                                  buttons=QtWidgets.QMessageBox.Close,
                                  parent=None
                                  )
            msg_box.exec_()


class CalibrateAutomaticWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        #self.resize(600, 100)

        self.layout = QGridLayout()  # Создание сетки - Основная

        # Блок нулевой
        self.nullblock = QtWidgets.QHBoxLayout()  # Создаем горизонтальный контейнер 1
        self.addr_IP = QtWidgets.QLabel('IP адрес устройства')
        self.addr_IP.setFont(QtGui.QFont("Times", 10))
        self.addr_IP.setFixedWidth(150)
        self.add_addr_IP = QtWidgets.QLineEdit()
        self.add_addr_IP.setFixedWidth(115)
        # self.add_addr_IP.setInputMask('DDD.999.999.999;#') # Убрать!
        self.add_addr_IP.setText('192.168.0.1')
        self.port_IP = QtWidgets.QLabel('Номер порта')
        self.port_IP.setFont(QtGui.QFont("Times", 10))
        self.port_IP.setFixedWidth(150)
        # self.port_IP.setContentsMargins(10, 0, 0, 0)
        self.add_port_IP = QtWidgets.QLineEdit()
        #self.port_IP.setContentsMargins(20,0,0,0)
        self.add_port_IP.setFixedWidth(50)
        self.add_port_IP.setInputMask('DDDD')
        self.add_port_IP.setText('1233')

        # Формирование интерфейса нулевого блока
        self.nullblock.addWidget(self.addr_IP, Qt.AlignJustify)
        self.nullblock.addWidget(self.add_addr_IP, Qt.AlignJustify)
        self.nullblock.addWidget(self.port_IP, Qt.AlignJustify)
        self.nullblock.addWidget(self.add_port_IP, Qt.AlignJustify)
        self.nullblock.addStretch(100)
        self.layout.addLayout(self.nullblock, 0, 0)
        self.layout.addWidget(QHLine(), 1, 0)  # ГОРИЗОНТАЛЬНЫЙ РАЗДЕЛИТЕЛЬ

        # Блок первый
        #self.layout.addWidget(self.nullblock,)
        self.layout.addWidget(self.channels_group(), 2, 0)
        self.layout.addWidget(self.step_group(), 2, 1)
        self.setWindowTitle('Автоматическая калибровка')






        # Блок второй
        self.twoblock = QtWidgets.QHBoxLayout()  # Создаем горизонтальный контейнер 1
        self.button_run_automatic_calibrate = QtWidgets.QPushButton("Запустить калибровку")
        self.button_run_automatic_calibrate.setFont(QtGui.QFont("Times", 10))
        self.button_run_automatic_calibrate.setFixedWidth(150)
        # Формирование интерфейса второго блока
        self.twoblock.addWidget(self.button_run_automatic_calibrate, Qt.AlignCenter)
        self.button_run_automatic_calibrate.clicked.connect(self.run_automatic_calibrate)

        #self.twoblock.addStretch(100)
        self.layout.addLayout(self.twoblock, 3, 0)

        # Третий блок с таблицей

        self.threeblock = QtWidgets.QHBoxLayout()
        self.table = QTableWidget()
        self.table.setColumnCount(7)

        # Set the table headers
        self.table.setHorizontalHeaderLabels(["Channel", "Voltage", "Vector", "Code_1", "Code_2", "Avg_Code", "K_calibrate",])

        #self.table.resizeColumnsToContents()
        self.threeblock.addWidget(self.table)
        self.layout.addLayout(self.threeblock, 4, 0)
        # Вывод содержимого сетки на экран
        self.setLayout(self.layout)


    def channels_group(self):
        groupBox = QGroupBox("Задайте уровни калибровки от наименьшего к наибольшему")
        groupBox.setFont(QtGui.QFont("Times", 10))
        #groupBox.resize(600,100)
        self.voltage_1_label = QtWidgets.QLabel('1 уровень,(В)')
        self.voltage_1 = QtWidgets.QLineEdit()
        self.voltage_1.setText('2')
        #self.voltage_1.setFixedWidth(30)

        self.voltage_2_label = QtWidgets.QLabel('2 уровень,(В)')
        self.voltage_2 = QtWidgets.QLineEdit()
        #self.voltage_2.setFixedWidth(30)
        self.voltage_2.setText('6')

        self.voltage_3_label = QtWidgets.QLabel('3 уровень,(В)')
        self.voltage_3 = QtWidgets.QLineEdit()
        #self.voltage_3.setFixedWidth(30)
        self.voltage_3.setText('10')

        self.voltage_4_label = QtWidgets.QLabel('4 уровень,(В)')
        self.voltage_4 = QtWidgets.QLineEdit()
        #self.voltage_4.setFixedWidth(30)
        self.voltage_4.setText('14')

        self.voltage_5_label = QtWidgets.QLabel('5 уровень,(В)')
        self.voltage_5 = QtWidgets.QLineEdit()
        #self.voltage_5.setFixedWidth(30)
        self.voltage_5.setText('18')

        self.voltage_6_label = QtWidgets.QLabel('6 уровень,(В)')
        self.voltage_6 = QtWidgets.QLineEdit()
        #self.voltage_6.setFixedWidth(30)
        self.voltage_6.setText('22')

        self.voltage_7_label = QtWidgets.QLabel('7 уровень,(В)')
        self.voltage_7 = QtWidgets.QLineEdit()
        #self.voltage_7.setFixedWidth(30)
        self.voltage_7.setText('24')

        self.voltage_8_label = QtWidgets.QLabel('8 уровень,(В)')
        self.voltage_8 = QtWidgets.QLineEdit()
        #self.voltage_8.setFixedWidth(30)
        self.voltage_8.setText('30')

        vbox_1 = QtWidgets.QVBoxLayout()
        vbox_2 = QtWidgets.QVBoxLayout()
        vbox_3 = QtWidgets.QVBoxLayout()
        vbox_4 = QtWidgets.QVBoxLayout()
        vbox_5 = QtWidgets.QVBoxLayout()
        vbox_6 = QtWidgets.QVBoxLayout()
        vbox_7 = QtWidgets.QVBoxLayout()
        vbox_8 = QtWidgets.QVBoxLayout()

        self.layout_2 = QGridLayout()  # Создание сетки - для уровней
        vbox_1.addWidget(self.voltage_1_label)
        vbox_1.addWidget(self.voltage_1)
        vbox_2.addWidget(self.voltage_2_label)
        vbox_2.addWidget(self.voltage_2)
        vbox_3.addWidget(self.voltage_3_label)
        vbox_3.addWidget(self.voltage_3)
        vbox_4.addWidget(self.voltage_4_label)
        vbox_4.addWidget(self.voltage_4)
        vbox_5.addWidget(self.voltage_5_label)
        vbox_5.addWidget(self.voltage_5)
        vbox_6.addWidget(self.voltage_6_label)
        vbox_6.addWidget(self.voltage_6)
        vbox_7.addWidget(self.voltage_7_label)
        vbox_7.addWidget(self.voltage_7)
        vbox_8.addWidget(self.voltage_8_label)
        vbox_8.addWidget(self.voltage_8)

        self.layout_2.addLayout(vbox_1, 0, 0)
        self.layout_2.addLayout(vbox_2, 0, 1)
        self.layout_2.addLayout(vbox_3, 0, 2)
        self.layout_2.addLayout(vbox_4, 0, 3)
        self.layout_2.addLayout(vbox_5, 0, 4)
        self.layout_2.addLayout(vbox_6, 0, 5)
        self.layout_2.addLayout(vbox_7, 0, 6)
        self.layout_2.addLayout(vbox_8, 0, 7)
        groupBox.setLayout(self.layout_2)

        return groupBox

    def step_group(self):
        groupBox = QGroupBox("Задайте шаг калибровки")
        groupBox.setFont(QtGui.QFont("Times", 10))

        self.step_label = QtWidgets.QLabel('Шаг калибровки')
        self.step = QtWidgets.QLineEdit()
        self.step.setText('1')
        #self.step.setFixedWidth(50)
        vbox_1 = QtWidgets.QVBoxLayout()
        vbox_1.addWidget(self.step_label)
        vbox_1.addWidget(self.step)
        groupBox.setLayout(vbox_1)
        return groupBox

    # def set_voltage(self):
    #     set_voltage = Calibrate()
    #     step = self.step.text()
    #     vector = self.vector_calibrate.text()
    #     channel = self.nmb_channel.text()
    #     if channel != '' and step != '':
    #         data = set_voltage.write_voltage_for_calibrate(step, vector, channel)
    #         self.dac_1.setText(hex(data[0]))
    #         self.dac_2.setText(hex(data[1]))
    #         self.voltage_1.setText(data[2])
    #         self.voltage_2.setText(data[3])
    #     else:
    #         msg_box = QMessageBox(QtWidgets.QMessageBox.Warning,
    #                               "Внимание!",
    #                               "Пожалуйста заполните поля 'Номера канала' и 'Шаг'",
    #                               buttons=QtWidgets.QMessageBox.Close,
    #                               parent=None
    #                               )
    #         msg_box.exec_()


    def run_automatic_calibrate(self):
        set_voltage = Calibrate()
        addr_IP = self.add_addr_IP.text()  # Получить введенное значение в поле
        port_IP = self.add_port_IP.text()  # Получить введенное значение в поле

        # Установка addr и port
        Ethernet.port = int(port_IP)
        Ethernet.host = str(addr_IP)

        step = int(self.step.text())
        volt_1 = self.voltage_1.text()
        volt_2 = self.voltage_2.text()
        volt_3 = self.voltage_3.text()
        volt_4 = self.voltage_4.text()
        volt_5 = self.voltage_5.text()
        volt_6 = self.voltage_6.text()
        volt_7 = self.voltage_7.text()
        volt_8 = self.voltage_8.text()

        voltages = [volt_1, volt_2, volt_3, volt_4, volt_5, volt_6, volt_7, volt_8]
        if step == '':
            msg_box = QMessageBox(QtWidgets.QMessageBox.Warning,
                                  "Внимание!",
                                  "Пожалуйста заполните поле калибровки",
                                  buttons=QtWidgets.QMessageBox.Close,
                                  parent=None
                                  )
            msg_box.exec_()
        # Задание COM порта
        com_port = SetVoltageRegulatorWindow(self)
        com_port.setWindowTitle('COM')
        com_port.exec_()

        count_voltage_step = 8 # так как 8 уровней напряжения
        count_channel_calibrate = 32*count_voltage_step
        #self.table.setRowCount(count_channel_calibrate)

        voltage_regutalor = VoltageRegulator()
        voltage_regutalor.set_port()

        for voltage in voltages:
            if voltage != '' and step != '':
                for channel in range(0, 32):
                    voltage_regutalor.set_voltage(int(voltage)) # управлять входным напряжением
                    # ЗДЕСЬ НАВЕРНОЕ ПРИДЕТСЯ СДЕЛАТЬ ЗАДЕРЖКУ на время нарастия напряжения на выходе регулятора
                    # В data_up и data_down будут содержаться результаты измерений
                    vector = 1
                    data_up = set_voltage.write_voltage_for_calibrate(step, vector, channel+1)
                    # ЗДЕСЬ НАВЕРНОЕ ПРИДЕТСЯ СДЕЛАТЬ ЗАДЕРЖКУ

                    self.table.setItem(channel, 0, QTableWidgetItem(str(channel)))
                    self.table.setItem(channel, 1, QTableWidgetItem(str(voltage)))
                    self.table.setItem(channel, 2, QTableWidgetItem(str(vector)))
                    self.table.setItem(channel, 3, QTableWidgetItem(str(data_up[0])))
                    self.table.setItem(channel, 4, QTableWidgetItem(str(data_up[1])))
                    average_code = (data_up[0]+data_up[1])/2
                    self.table.setItem(channel, 5, QTableWidgetItem(str(average_code)))
                    k_calibrate = 0
                    self.table.setItem(channel, 6, QTableWidgetItem(str(k_calibrate)))

                    vector = 0
                    data_down = set_voltage.write_voltage_for_calibrate(step, vector, channel+1)
                    # ЗДЕСЬ НАВЕРНОЕ ПРИДЕТСЯ СДЕЛАТЬ ЗАДЕРЖКУ

                    self.table.setItem(channel+1, 0, QTableWidgetItem(str(channel)))
                    self.table.setItem(channel+1, 1, QTableWidgetItem(str(voltage)))
                    self.table.setItem(channel+1, 2, QTableWidgetItem(str(vector)))
                    self.table.setItem(channel+1, 3, QTableWidgetItem(str(data_up[0])))
                    self.table.setItem(channel+1, 4, QTableWidgetItem(str(data_up[1])))
                    average_code = (data_up[0]+data_up[1])/2
                    self.table.setItem(channel+1, 5, QTableWidgetItem(str(average_code)))
                    k_calibrate = 0
                    self.table.setItem(channel+1, 6, QTableWidgetItem(str(k_calibrate)))


class SetVoltageRegulatorWindow(QtWidgets.QDialog):
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
        for port in serial_ports():
            self.combo_box_1.addItem(port)
            self.combo_box_1.setInsertPolicy(0)
        self.speeds = VoltageRegulator().speeds
        for speed in self.speeds:
            self.combo_box_2.addItem(speed)
            self.combo_box_2.setCurrentText('9600')
            self.combo_box_2.setInsertPolicy(0)

        self.button_write_settings = QtWidgets.QPushButton("Установить настройки")
        self.button_write_settings.setFont(QtGui.QFont("Times", 10))
        self.button_write_settings.setFixedWidth(150)
        # Формирование интерфейса второго блока
        self.oneblock.addWidget(self.combo_box_1, Qt.AlignCenter)
        self.oneblock.addWidget(self.combo_box_2, Qt.AlignCenter)
        self.oneblock.addWidget(self.button_write_settings, Qt.AlignCenter)
        self.button_write_settings.clicked.connect(self.set_com_port)
        self.layout.addLayout(self.oneblock, 1, 0)

        self.setLayout(self.layout)

    def set_com_port(self):
        port = self.combo_box_1.currentText()
        speed = self.combo_box_2.currentText()
        VoltageRegulator.port = port
        VoltageRegulator.speed = speed
        self.close()



