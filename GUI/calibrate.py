from GUI.grafics import GraficWindow
from GwInstek74303S.GUI.GwINSTEK import *
from base_interface_function import *
from export import *
from datetime import datetime
from GUI.central_window import QHLine
from PyQt5 import QtWidgets, QtGui, QtCore
from special_interface_function import *
from stages import Calibrate, CompareLevel
from globus_ethernet import Ethernet
from loggings import *


# class CalibrateThread(QtCore.QThread):
#     thread_signal = QtCore.pyqtSignal(int)
#     thread_data = QtCore.pyqtSignal(list, int, int, str)
#     count_voltage_step = 8  # так как 8 напряжений калибровки калибровки
#     count_channel_calibrate = 32  # Вернуть 32.
#
#
#     def __init__(self, parent=None):
#         #self.running = False  # Флаг выполнения
#         QtCore.QThread.__init__(self, parent)
#
#     def run(self):
#         set_voltage = Calibrate()
#         voltages = CalibrateAutomaticWindow.voltages  # Получить напряжение из формы
#         step = CalibrateAutomaticWindow.step          # Получить шаг из формы
#
#         voltage_regulator = VoltageRegulator()  # Создать объект Regulator
#         voltage_regulator.set_port()  # Задать порт
#         voltage_regulator.power_em()  # Подать питание
#
#         # self.table.setRowCount(count_channel_calibrate)
#
#         i = 0
#         for voltage in voltages:
#             voltage_regulator.set_calibrate_voltage(float(voltage))  # управлять входным напряжением
#             for channel in range(0, self.count_channel_calibrate):
#                 if float(voltage) < 15.0:
#                     # В data будут содержаться результаты измерений
#                     vector = 0
#                     data = set_voltage.write_voltage_for_calibrate(step, vector, (channel + 1))
#                     self.thread_data.emit(data, channel, vector, voltage)
#                 else:
#                     # В data будут содержаться результаты измерений
#                     vector = 0
#                     data = set_voltage.write_voltage_for_calibrate(step, vector, (channel + 1))
#                     self.thread_data.emit(data, channel, vector, voltage)
#                 i += 1
#                 self.thread_signal.emit(i)  # Для прогрессбара
#         voltage_regulator.power(0)          # Выключить питание после выполнения калибровки


class CalibrateThread(QtCore.QThread):
    thread_signal = QtCore.pyqtSignal(int)
    thread_data = QtCore.pyqtSignal(list, int, int, str)
    count_voltage_step = 8  # так как 8 напряжений калибровки калибровки
    count_channel_calibrate = 32  # Вернуть 32.

    def __init__(self, parent=None):
        # self.running = False  # Флаг выполнения
        QtCore.QThread.__init__(self, parent)

    def run(self):
        # set_voltage = Calibrate()
        voltages = CalibrateAutomaticWindow.voltages  # Получить напряжение из формы
        step = CalibrateAutomaticWindow.step  # Получить шаг из формы

        voltage_regulator = VoltageRegulator()  # Создать объект Regulator
        voltage_regulator.set_port()  # Задать порт
        voltage_regulator.power_em()  # Подать питание
        # self.table.setRowCount(count_channel_calibrate)

        i = 0

        k_transformation = 11.05  # Расчетный коэффициент трансформации
        bit_depth_DAC = 12  # Разрядность ЦАПа
        ref_voltage = 3.3
        max_code_DAC = (2 ** bit_depth_DAC) - 1  # Максимальный код ЦАПа
        reference_voltage = ref_voltage / max_code_DAC  # 1 единица кода, Вольт
        number_of_successful_operations = 25  # Задаем число успешных чтений подряд
        # flag_search_voltage = False
        levels = []
        compare = CompareLevel()

        def mask_channel(channel):
            int_mask_channels = round(2 ** int(channel))
            mask_channels = [0] * 4
            if int_mask_channels < 255:
                mask_channels[0:4] = int_mask_channels, 0, 0, 0
            if 255 < int_mask_channels < 65535:
                rez = int_mask_channels.to_bytes((int_mask_channels.bit_length() + 7) // 8, 'little')
                mask_channels[0:4] = rez[0], rez[1], 0, 0
            if 65535 < int_mask_channels < 16777215:
                rez = int_mask_channels.to_bytes((int_mask_channels.bit_length() + 7) // 8, 'little')
                mask_channels[0:4] = rez[0], rez[1], rez[2], 0
            if 16777215 < int_mask_channels < 4294967295:
                rez = int_mask_channels.to_bytes((int_mask_channels.bit_length() + 7) // 8, 'little')
                mask_channels[0:4] = rez[0], rez[1], rez[2], rez[3]
            return mask_channels

        # Здесь блок кода для запроса температуры с датчика
        write = request_temperature()
        Ethernet().swap(write)
        time.sleep(3.0)
        Ethernet().swap(write)
        write = data_request(0)
        data = Ethernet().swap(write)
        rez_temp = data[1][-4:]
        rez_temp = rez_temp[0:3]
        if rez_temp[0] == 1:
            int_temp = -(int.from_bytes(rez_temp[1:3], byteorder='little') + 1) * 0.0625
            print(f'Температура: {int_temp}')
        else:
            int_temp = int.from_bytes(rez_temp[1:3], byteorder='little') * 0.0625
            print(f'Температура: {int_temp}')



        for voltage in voltages:
            # Должно быть с 0, поставил с 4 для отладки, так как кривые импульсы
            for channel in range(0, self.count_channel_calibrate):
                # Для 1 компаратора выключение
                off_voltage_comp_1 = float(
                    voltage)  # Задал верхний уровень, так как в реальности напряжение будет меньше
                off_voltage_comp_2 = float(voltage)
                down_voltage_1 = float(voltage) / 2  # Задал половину уровня, так как коэфф. калибровки
                #  в реальности не должен быть равен 2
                count_comp_1 = 0
                count_comp_2 = 0
                voltage_regulator.set_calibrate_voltage(float(voltage))  # Задаем напряжение на источнике, в первый раз
                while True:
                    off_voltage_comp_1 = round(off_voltage_comp_1, 2)
                    off_voltage_comp_2 = round(off_voltage_comp_2, 2)
                    channel_volt = {str(channel + 1): [off_voltage_comp_1, off_voltage_comp_2]}  # Формирование уровней
                    logs = compare.compare_level(0, **channel_volt)  # Выполнение разового компарирования
                    # log_1 = int.from_bytes(logs[0][0], byteorder='big', signed=True)
                    # Маска контролируемых каналов побитово
                    mask_channels = mask_channel(channel)
                    mask_comp_1 = [0] * 4
                    mask_comp_2 = [0] * 4
                    for i in range(0, 4):
                        mask_comp_1[i] = logs[0][0][i] & mask_channels[i]
                        mask_comp_2[i] = logs[0][1][i] & mask_channels[i]
                    if mask_comp_1 == mask_channels:
                        count_comp_1 += 1
                    else:
                        count_comp_1 = 0
                        off_voltage_comp_1 -= step / 100

                    if mask_comp_2 == mask_channels:
                        count_comp_2 += 1
                    else:
                        count_comp_2 = 0
                        off_voltage_comp_2 -= step / 100

                    if count_comp_1 >= number_of_successful_operations and \
                            count_comp_2 >= number_of_successful_operations:  # Количество успешных срабатываний подряд
                        levels.append(channel_volt)  # Запомним в список текущий уровень срабатывания
                        add_log_file(
                            f'Уровень 1 (1 компаратор) для {voltage}(В) срабатывания - на выключение канала {channel + 1}'
                            f' равен {off_voltage_comp_1}(В)')
                        add_log_file(
                            f'Уровень 1 (2 компаратор) для {voltage}(В) срабатывания - на выключение канала {channel + 1}'
                            f' равен {off_voltage_comp_2}(В)')
                        break

                    if off_voltage_comp_1 <= down_voltage_1 or off_voltage_comp_2 <= down_voltage_1:
                        levels.append({str(channel + 1): [0, 0]})
                        add_log_file(f'Уровень 1 для {voltage}(В) срабатывания - на выключение канала {channel + 1}'
                                     f' не найден')
                        break

                # Для включения
                up_voltage_2_1 = float(voltage)  # Задал верхний уровень, так как в реальности напряжение будет меньше
                on_voltage_comp_1 = off_voltage_comp_1  # Задал уровень из верхнего цикла, считаем что он был выключен теперь
                # включаем
                on_voltage_comp_2 = off_voltage_comp_2
                count_comp_1 = 0
                count_comp_2 = 0

                while True:
                    on_voltage_comp_1 = round(on_voltage_comp_1, 2)
                    on_voltage_comp_2 = round(on_voltage_comp_2, 2)

                    channel_volt = {str(channel + 1): [on_voltage_comp_1, on_voltage_comp_2]}
                    logs = compare.compare_level(0, **channel_volt)  # Выполнение разового компарирования

                    # Маска контролируемых каналов побитово
                    mask_channels = mask_channel(channel)
                    mask_comp_1 = [0] * 4
                    mask_comp_2 = [0] * 4

                    for i in range(0, 4):
                        mask_comp_1[i] = logs[0][0][i] & mask_channels[i]
                        mask_comp_2[i] = logs[0][1][i] & mask_channels[i]

                    if mask_comp_1 != mask_channels:
                        count_comp_1 += 1
                    else:
                        count_comp_1 = 0
                        on_voltage_comp_1 += step / 100

                    if mask_comp_2 != mask_channels:
                        count_comp_2 += 1
                    else:
                        count_comp_2 = 0
                        on_voltage_comp_2 += step / 100

                    if count_comp_1 >= number_of_successful_operations and \
                            count_comp_2 >= number_of_successful_operations:  # Количество успешных срабатываний подряд
                        levels.append(channel_volt)  # Запомним в список текущий уровень срабатывания
                        add_log_file(
                            f'Уровень 2 (1 компаратор) для {voltage}(В) срабатывания - на включение канала {channel + 1}'
                            f' равен {on_voltage_comp_1}(В)')
                        add_log_file(
                            f'Уровень 2 (2 компаратор) для {voltage}(В) срабатывания - на включение канала {channel + 1}'
                            f' равен {on_voltage_comp_2}(В)')
                        break

                    if on_voltage_comp_1 >= up_voltage_2_1 or on_voltage_comp_1 >= up_voltage_2_1:
                        levels.append({str(channel + 1): [0, 0]})
                        add_log_file(f'Уровень 2 для {voltage}(В) срабатывания - на включение канала {channel + 1}'
                                     f' не найден')
                        break

                code_dac_1_low_1 = round(off_voltage_comp_1 / k_transformation / reference_voltage)
                code_dac_2_low_2 = round(off_voltage_comp_2 / k_transformation / reference_voltage)
                code_dac_1_up_1 = round(on_voltage_comp_1 / k_transformation / reference_voltage)
                code_dac_2_up_2 = round(on_voltage_comp_2 / k_transformation / reference_voltage)
                self.thread_data.emit([0, 0, code_dac_1_low_1, code_dac_2_low_2,
                                       code_dac_1_up_1, code_dac_2_up_2, int_temp], channel, 0, voltage)
            i += 1
            self.thread_signal.emit(i)  # Для прогрессбара
        voltage_regulator.power(0)  # Выключить питание после выполнения калибровки


class CalibrateWindow(QtWidgets.QWidget):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout()  # Создание сетки - Основная
        self.setWindowTitle('Ручная калибровка')
        self.setFont(QtGui.QFont("Times", 10))

        # Блок нулевой
        self.nullblock = QtWidgets.QHBoxLayout()  # Создаем горизонтальный контейнер 1
        self.addr_IP = QtWidgets.QLabel('IP адрес устройства')
        self.addr_IP.setFont(QtGui.QFont("Times", 10))
        self.addr_IP.setFixedWidth(150)
        self.add_addr_IP = QtWidgets.QLineEdit()
        self.add_addr_IP.setFixedWidth(115)
        # self.add_addr_IP.setInputMask('DDD.999.999.999;#') # Убрать!
        self.add_addr_IP.setText('192.168.1.0')
        self.port_IP = QtWidgets.QLabel('Номер порта')
        self.port_IP.setFont(QtGui.QFont("Times", 10))
        self.port_IP.setFixedWidth(150)
        # self.port_IP.setContentsMargins(10, 0, 0, 0)
        self.add_port_IP = QtWidgets.QLineEdit()
        # self.port_IP.setContentsMargins(20,0,0,0)
        self.add_port_IP.setFixedWidth(50)
        self.add_port_IP.setInputMask('DDDD')
        self.add_port_IP.setText('1233')

        # Формирование интерфейса нулевого блока
        self.nullblock.addWidget(self.addr_IP, Qt.AlignJustify)
        self.nullblock.addWidget(self.add_addr_IP, Qt.AlignJustify)
        self.nullblock.addWidget(self.port_IP, Qt.AlignJustify)
        self.nullblock.addWidget(self.add_port_IP, Qt.AlignJustify)
        self.nullblock.addStretch()
        self.layout.addLayout(self.nullblock, 0, 0)
        self.layout.addWidget(QHLine(), 1, 0)  # ГОРИЗОНТАЛЬНЫЙ РАЗДЕЛИТЕЛЬ

        # Блок первый
        self.oneblock = QtWidgets.QHBoxLayout()  # Создаем горизонтальный контейнер 1

        self.nmb_label = QtWidgets.QLabel("Номер канала")
        self.nmb_channel = QtWidgets.QLineEdit()
        self.nmb_channel.setText('1')
        self.nmb_channel.setFixedWidth(50)

        self.step_label = QtWidgets.QLabel('Шаг')
        self.step = QtWidgets.QLineEdit()
        self.step.setText('1')
        self.step.setFixedWidth(50)

        self.vector_label = QtWidgets.QLabel('Направление калибровки')
        self.vector_calibrate = QtWidgets.QLineEdit()
        self.vector_calibrate.setFixedWidth(50)
        self.vector_calibrate.setText('1')

        self.voltage_label = QtWidgets.QLabel('Напряжение калибровки')
        self.voltage_calibrate = QtWidgets.QLineEdit()
        self.voltage_calibrate.setFixedWidth(50)
        self.voltage_calibrate.setText('26')

        self.button_write_voltage = QtWidgets.QPushButton("Установить напряжение")
        self.button_write_voltage.setFixedWidth(200)

        # Фомирование первого блока интерфейса

        self.oneblock.addWidget(self.nmb_label, Qt.AlignLeft)
        self.oneblock.addWidget(self.nmb_channel, Qt.AlignLeft)
        self.oneblock.addWidget(self.step_label, Qt.AlignLeft)
        self.oneblock.addWidget(self.step, Qt.AlignJustify)
        self.oneblock.addWidget(self.vector_label, Qt.AlignJustify)
        self.oneblock.addWidget(self.vector_calibrate, Qt.AlignJustify)
        self.oneblock.addWidget(self.voltage_label, Qt.AlignJustify)
        self.oneblock.addWidget(self.voltage_calibrate, Qt.AlignJustify)
        self.oneblock.addWidget(self.button_write_voltage, Qt.AlignJustify)
        self.button_write_voltage.clicked.connect(self.set_voltage)

        self.oneblock.addStretch(100)
        self.layout.addLayout(self.oneblock, 2, 0, 1, 0)

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
        self.layout.addLayout(self.twoblock, 3, 0, 1, 0)

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
        self.layout.addLayout(self.treeblock, 4, 0, 1, 0)

        # Вывод содержимого сетки на экран
        self.setLayout(self.layout)

    def set_voltage(self):
        # set_voltage = Calibrate()
        addr_IP = self.add_addr_IP.text()  # Получить введенное значение в поле
        port_IP = self.add_port_IP.text()  # Получить введенное значение в поле
        voltage = self.voltage_calibrate.text()
        # Установка addr и port
        Ethernet.port = int(port_IP)
        Ethernet.host = str(addr_IP)
        if GwINSTEKWindow.flag_setting == 0:  # Чтобы второй раз при повторе не выбирать COM
            # Задание COM порта
            com_port = GwINSTEKWindow(self)
            com_port.setWindowTitle('COM')
            com_port.exec_()

        voltage_regulator = VoltageRegulator()  # Создать объект Regulator
        # if GwINSTEKWindow.flag_setting == 0:  # Чтобы второй раз не устанавливать настройки COM
        voltage_regulator.set_port()  # Задать порт
        voltage_regulator.set_calibrate_voltage(float(voltage))  # управлять входным напряжением

        set_voltage = Calibrate()
        step = int(self.step.text())
        vector = int(self.vector_calibrate.text())
        channel = int(self.nmb_channel.text())

        if channel != '' and step != '' and voltage != '':
            voltage_regulator.power_em()  # Подать питание
            # write = reset_em(1)
            # Ethernet().delay_swap(write)
            voltage_regulator.set_calibrate_voltage(float(voltage))  # управлять входным напряжением
            data = set_voltage.write_voltage_for_calibrate(step, vector, channel)
            self.dac_1.setText(str(data[0]))
            self.dac_2.setText(str(data[1]))
            self.voltage_1.setText(str(data[2]))
            self.voltage_2.setText(str(data[3]))
            voltage_regulator.power(0)  # Выключить источник питания
        else:
            msg_box = QMessageBox(QtWidgets.QMessageBox.Warning,
                                  "Внимание!",
                                  "Пожалуйста заполните все поля'",
                                  buttons=QtWidgets.QMessageBox.Close,
                                  parent=None
                                  )
            msg_box.exec_()


class CalibrateAutomaticWindow(QtWidgets.QWidget):
    voltages = [0, 0, 0, 0, 0, 0, 0, 0]
    step = 0
    counter = 0
    table_df = 0

    # Создание пустого массива размером 32 - каналы - 8 уровни напряжений
    # np.zeros((32, 8))

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.resize(600, 100)
        self.counter = 0
        self.layout = QGridLayout()  # Создание сетки - Основная

        # Блок нулевой
        self.nullblock = QtWidgets.QHBoxLayout()  # Создаем горизонтальный контейнер 1
        self.addr_IP = QtWidgets.QLabel('IP адрес устройства')
        self.addr_IP.setFont(QtGui.QFont("Times", 10))
        self.addr_IP.setFixedWidth(150)
        self.add_addr_IP = QtWidgets.QLineEdit()
        self.add_addr_IP.setFixedWidth(115)
        # self.add_addr_IP.setInputMask('DDD.999.999.999;#') # Убрать!
        self.add_addr_IP.setText('192.168.1.0')
        self.port_IP = QtWidgets.QLabel('Номер порта')
        self.port_IP.setFont(QtGui.QFont("Times", 10))
        self.port_IP.setFixedWidth(150)
        # self.port_IP.setContentsMargins(10, 0, 0, 0)
        self.add_port_IP = QtWidgets.QLineEdit()
        # self.port_IP.setContentsMargins(20,0,0,0)
        self.add_port_IP.setFixedWidth(50)
        self.add_port_IP.setInputMask('DDDD')
        self.add_port_IP.setText('1233')

        # Формирование интерфейса нулевого блока
        self.nullblock.addWidget(self.addr_IP, Qt.AlignJustify)
        self.nullblock.addWidget(self.add_addr_IP, Qt.AlignJustify)
        self.nullblock.addWidget(self.port_IP, Qt.AlignJustify)
        self.nullblock.addWidget(self.add_port_IP, Qt.AlignJustify)
        self.nullblock.addStretch()
        self.layout.addLayout(self.nullblock, 0, 0)
        self.layout.addWidget(QHLine(), 1, 0)  # ГОРИЗОНТАЛЬНЫЙ РАЗДЕЛИТЕЛЬ

        # Блок первый
        self.layout.addWidget(self.channels_group(), 2, 0)
        self.layout.addWidget(self.step_group(), 2, 1)
        self.setWindowTitle('Автоматическая калибровка')

        # Блок второй
        self.twoblock = QtWidgets.QHBoxLayout()  # Создаем горизонтальный контейнер 1
        self.button_comport = QtWidgets.QPushButton("Настройка COM-порта")
        self.button_comport.setFont(QtGui.QFont("Times", 10))
        self.button_comport.setFixedWidth(200)
        self.button_run_automatic_calibrate = QtWidgets.QPushButton("Начать калибровку")
        self.button_run_automatic_calibrate.setFont(QtGui.QFont("Times", 10))
        self.button_run_automatic_calibrate.setFixedWidth(200)

        # Формирование интерфейса второго блока
        self.twoblock.addWidget(self.button_comport, Qt.AlignCenter)
        self.twoblock.addWidget(self.button_run_automatic_calibrate, Qt.AlignCenter)
        self.button_comport.clicked.connect(self.run_automatic_calibrate)
        self.button_run_automatic_calibrate.clicked.connect(self.run_thread)

        # self.twoblock.addStretch(100)
        self.layout.addLayout(self.twoblock, 3, 0)

        # Третий блок с таблицей
        self.threeblock = QtWidgets.QHBoxLayout()
        self.table = QTableWidget(256, 14)  # Второе число кол-во столбцов
        self.vbox = QtWidgets.QVBoxLayout()

        self.button_export = QtWidgets.QPushButton("Экспорт в *.xlsx")
        self.button_export.setFont(QtGui.QFont("Times", 10))
        self.button_export.setFixedWidth(200)
        self.button_export.clicked.connect(self.export_calibrate)
        self.button_export.setEnabled(False)  # Заблокировать кнопку

        self.button_write_k_polinoms = QtWidgets.QPushButton("Записать коэффициенты в ПЗУ")
        self.button_write_k_polinoms.setFont(QtGui.QFont("Times", 10))
        self.button_write_k_polinoms.setFixedWidth(200)
        self.button_write_k_polinoms.clicked.connect(self.write_k_polinoms)
        self.button_write_k_polinoms.setEnabled(True)  # Заблокировать кнопку

        self.button_graf = QtWidgets.QPushButton("Показать график")
        self.button_graf.setFont(QtGui.QFont("Times", 10))
        self.button_graf.setFixedWidth(200)
        self.button_graf.clicked.connect(self.graf_calibrate)
        self.button_graf.setEnabled(False)  # Заблокировать кнопку

        self.vbox.addWidget(self.button_write_k_polinoms)
        self.vbox.addWidget(self.button_export)
        self.vbox.addWidget(self.button_graf)
        self.vbox.addStretch()  # Пружина

        # Set the table headers
        self.table.setHorizontalHeaderLabels(["N", "Channel", "Voltage", "Vector",
                                              "Code_1_LOW", "Code_1_UP", "Avg_1_CODE",
                                              "Code_2_LOW", "Code_2_UP", "Avg_2_CODE",
                                              "K_calibrate_1", "K_calibrate_2", "K_calibrate_Avg", "Temp"])

        # self.table.resizeColumnsToContents()
        self.threeblock.addWidget(self.table)
        self.layout.addLayout(self.threeblock, 4, 0)
        self.layout.addLayout(self.vbox, 4, 1)

        # Ниже описание и настройка потока для работы с ЭМ1
        self.automatic_calibrate_thread = CalibrateThread()  # Содаем экземпляр класса StageThread
        self.automatic_calibrate_thread.started.connect(self.on_started)
        self.automatic_calibrate_thread.thread_signal.connect(self.on_change, QtCore.Qt.QueuedConnection)
        self.automatic_calibrate_thread.thread_data.connect(self.table_update, QtCore.Qt.QueuedConnection)
        self.automatic_calibrate_thread.finished.connect(self.on_finished)

        # sub.setWidget(self.setLayout(self.layout))

        # Пятый блок
        # Ниже создан прогресс бар
        self.fourblock = QtWidgets.QHBoxLayout()
        self.progress_bar = QtWidgets.QProgressBar()
        count = CalibrateThread.count_channel_calibrate * CalibrateThread.count_voltage_step
        self.progress_bar.setRange(0, count)
        self.fourblock.addWidget(self.progress_bar)
        self.layout.addLayout(self.fourblock, 5, 0)

        # Вывод содержимого сетки на экран
        self.setLayout(self.layout)

    def channels_group(self):
        groupBox = QGroupBox("Задайте уровни калибровки от наименьшего к наибольшему")
        groupBox.setFont(QtGui.QFont("Times", 10))
        # groupBox.resize(600,100)
        self.voltage_1_label = QtWidgets.QLabel('1 уровень,(В)')
        self.voltage_1 = QtWidgets.QLineEdit()
        self.voltage_1.setText('2')
        # self.voltage_1.setFixedWidth(30)

        self.voltage_2_label = QtWidgets.QLabel('2 уровень,(В)')
        self.voltage_2 = QtWidgets.QLineEdit()
        # self.voltage_2.setFixedWidth(30)
        self.voltage_2.setText('6')

        self.voltage_3_label = QtWidgets.QLabel('3 уровень,(В)')
        self.voltage_3 = QtWidgets.QLineEdit()
        # self.voltage_3.setFixedWidth(30)
        self.voltage_3.setText('10')

        self.voltage_4_label = QtWidgets.QLabel('4 уровень,(В)')
        self.voltage_4 = QtWidgets.QLineEdit()
        # self.voltage_4.setFixedWidth(30)
        self.voltage_4.setText('14')

        self.voltage_5_label = QtWidgets.QLabel('5 уровень,(В)')
        self.voltage_5 = QtWidgets.QLineEdit()
        # self.voltage_5.setFixedWidth(30)
        self.voltage_5.setText('18')

        self.voltage_6_label = QtWidgets.QLabel('6 уровень,(В)')
        self.voltage_6 = QtWidgets.QLineEdit()
        # self.voltage_6.setFixedWidth(30)
        self.voltage_6.setText('22')

        self.voltage_7_label = QtWidgets.QLabel('7 уровень,(В)')
        self.voltage_7 = QtWidgets.QLineEdit()
        # self.voltage_7.setFixedWidth(30)
        self.voltage_7.setText('26')

        self.voltage_8_label = QtWidgets.QLabel('8 уровень,(В)')
        self.voltage_8 = QtWidgets.QLineEdit()
        # self.voltage_8.setFixedWidth(30)
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
        groupBox.setFixedWidth(200)
        self.step_label = QtWidgets.QLabel('Шаг калибровки')
        self.step = QtWidgets.QLineEdit()
        self.step.setText('1')
        self.step.setFixedWidth(50)
        vbox_1 = QtWidgets.QVBoxLayout()
        vbox_1.addWidget(self.step_label)
        vbox_1.addWidget(self.step)
        groupBox.setLayout(vbox_1)

        return groupBox

    def run_automatic_calibrate(self):
        addr_IP = self.add_addr_IP.text()  # Получить введенное значение в поле
        port_IP = self.add_port_IP.text()  # Получить введенное значение в поле

        # Установка addr и port
        Ethernet.port = int(port_IP)
        Ethernet.host = str(addr_IP)

        CalibrateAutomaticWindow.step = int(self.step.text())
        volt_1 = self.voltage_1.text()
        volt_2 = self.voltage_2.text()
        volt_3 = self.voltage_3.text()
        volt_4 = self.voltage_4.text()
        volt_5 = self.voltage_5.text()
        volt_6 = self.voltage_6.text()
        volt_7 = self.voltage_7.text()
        volt_8 = self.voltage_8.text()

        CalibrateAutomaticWindow.voltages = [volt_1, volt_2, volt_3, volt_4, volt_5, volt_6, volt_7, volt_8]
        if self.step == '':
            msg_box = QMessageBox(QtWidgets.QMessageBox.Warning,
                                  "Внимание!",
                                  "Пожалуйста заполните поле калибровки",
                                  buttons=QtWidgets.QMessageBox.Close,
                                  parent=None
                                  )
            msg_box.exec_()
        # Задание COM порта
        com_port = GwINSTEKWindow(self)
        com_port.setWindowTitle('COM')
        com_port.exec_()

    def on_started(self):  # Запускается в начале потока
        self.start_time = datetime.datetime.now()

    def on_finished(self):  # Запускается после окончания выполнения потока просто для наглядности
        msg_box = QMessageBox(QtWidgets.QMessageBox.Information,
                              "Калибровка окончена!",
                              "Время калибровки: {} ".format((datetime.datetime.now() - self.start_time)),
                              buttons=QtWidgets.QMessageBox.Close,
                              parent=None
                              )
        msg_box.exec_()
        self.return_table()
        self.button_export.setEnabled(True)  # Разблокировать кнопку
        self.button_graf.setEnabled(True)  # Разблокировать кнопку
        self.button_write_k_polinoms.setEnabled(True)  # Разблокировать кнопку
        # self.automatic_calibrate_thread.yieldCurrentThread()  # Принудительное завершение потока

    def on_change(self, i):  # Принимаем число из потока в Progressbar
        self.progress_bar.setValue(i)

    def run_thread(self):
        if not self.automatic_calibrate_thread.isRunning():
            self.automatic_calibrate_thread.start()  # Запускаем поток

    def table_update(self, data, number, vector, voltage):
        self.channel = int(number)
        self.table.setItem((32 * self.counter) + number, 0, QTableWidgetItem(str((32 * self.counter) + number)))
        self.table.setItem((32 * self.counter) + number, 1, QTableWidgetItem(str(self.channel + 1)))
        self.table.setItem((32 * self.counter) + number, 2, QTableWidgetItem(str(voltage)))
        self.table.setItem((32 * self.counter) + number, 3, QTableWidgetItem(str(vector)))
        self.table.setItem((32 * self.counter) + number, 4, QTableWidgetItem(str(int(data[2]))))
        self.table.setItem((32 * self.counter) + number, 5, QTableWidgetItem(str(int(data[4]))))
        self.table.setItem((32 * self.counter) + number, 7, QTableWidgetItem(str(int(data[3]))))
        self.table.setItem((32 * self.counter) + number, 8, QTableWidgetItem(str(int(data[5]))))
        average_code_1 = (data[2] + data[4]) / 2
        self.table.setItem((32 * self.counter) + number, 6, QTableWidgetItem(str(average_code_1)))
        average_code_2 = (data[3] + data[5]) / 2
        self.table.setItem((32 * self.counter) + number, 9, QTableWidgetItem(str(average_code_2)))

        try:
            k_calibrate_1 = (float(voltage) / 11.05) / ((3.3 * round(average_code_1)) / 4095)
        except ZeroDivisionError:
            k_calibrate_1 = 0
        self.table.setItem((32 * self.counter) + number, 10, QTableWidgetItem(format(k_calibrate_1, '.2f')))
        try:
            k_calibrate_2 = (float(voltage) / 11.05) / ((3.3 * round(average_code_2)) / 4095)
        except ZeroDivisionError:
            k_calibrate_2 = 0
        self.table.setItem((32 * self.counter) + number, 11, QTableWidgetItem(format(k_calibrate_2, '.2f')))
        try:
            k_calibrate_avg = round((k_calibrate_1 + k_calibrate_2) / 2, 2)
        except ZeroDivisionError:
            k_calibrate_avg = 0
        self.table.setItem((32 * self.counter) + number, 12, QTableWidgetItem(format(k_calibrate_avg, '.2f')))
        self.table.setItem((32 * self.counter) + number, 13, QTableWidgetItem(format(data[6], '.2f')))
        if number == 31:
            self.counter += 1

    def write_k_polinoms(self):
        voltage_regulator = VoltageRegulator()  # Создать объект Regulator
        voltage_regulator.set_port()  # Задать порт
        voltage_regulator.power_em()  # Подать питание
        # rows = self.table.rowCount()
        # k_polinoms = []
        # for i in range(0, rows):
        #     if self.table.model().index(i, 10).data() is None:
        #         k_polinoms.append(float(0))
        #         # где 10 - индекс столбца K_kalibrate_1 в таблице table
        #     else:
        #         k_polinoms.append(float(self.table.model().index(i, 10).data()))
        #         # где 10 - индекс столбца K_kalibrate_1 в таблице table
        #
        # for i in range(0, rows):
        #     if self.table.model().index(i, 11).data() is None:
        #         k_polinoms.append(float(0))  # где 11 - индекс столбца K_kalibrate_2 в таблице table
        #     else:
        #         k_polinoms.append(float(self.table.model().index(i, 11).data()))
        #         # где 11 - индекс столбца K_kalibrate_2 в таблице table

        write_rom = write_k_polinoms()  # Запись в ПЗУ
        add_log_file("Запись калибровочных коэффициентов")
        data = Ethernet().swap(write_rom)
        add_log_file(data[0])  # Запись в лог, какие коэффициенты записали
        write = reset_em(1)  # Исходное Hard
        Ethernet().delay_swap(write)

        write = read_k_polinoms()  # Чтение калибровочных коэффициентов
        Ethernet().swap(write)
        write = data_request(0)  # Запрос данных (калибровочных коэффициентов)
        data = Ethernet().swap(write)
        add_log_file("Чтение калибровочных коэффициентов")
        add_log_file(data[1])  # Запись коэффициентов в лог

        # 8 байт - Frame, 24 байта - любых см. команду write_k_kalibrate()
        undefined_bytes = 24  # Было 24 - решил убрать для экономии памяти
        k_polinoms = data[1][22 + 8 + undefined_bytes:]
        # Выцепляем из команды записанные коэффициенты
        write_massive_k_kalibrate = write_rom[2 + undefined_bytes:]
        valid = True
        for i in range(0, len(write_massive_k_kalibrate)):
            if (k_polinoms[i]) != write_massive_k_kalibrate[i]:
                valid = False

        if valid == True:
            msg_box = QMessageBox(QtWidgets.QMessageBox.Information,
                                  "Запись коээфициентов выполнена:",
                                  "Успешно!",
                                  buttons=QtWidgets.QMessageBox.Close,
                                  parent=None
                                  )
        else:
            msg_box = QMessageBox(QtWidgets.QMessageBox.Information,
                                  "Запись коээфициентов выполнена:",
                                  "Неуспешно! \n"
                                  "Для более подробной информации смотрите лог-файл",
                                  buttons=QtWidgets.QMessageBox.Close,
                                  parent=None
                                  )
        msg_box.exec_()
        voltage_regulator.power(0)

    def closeEvent(self, event):
        self.hide()  # Скрываем окно
        self.automatic_calibrate_thread.wait(2000)  # Время чтобы закончить
        event.accept()  # Закрываем окно

    def export_calibrate(self):
        exportToExcel(self)

    def graf_calibrate(self):
        grafic_window = GraficWindow()
        grafic_window.show()
        grafic_window.exec_()  # Не знаю как, но это работает

    def return_table(self):
        data_voltage = [self.table.item(row, 2).text()  # 2 - столбец с напряжением
                        for row in range(self.table.rowCount())
                        if self.table.item(row, 2) is not None]  # 2 - столбец с напряжением

        data_k_calibrate_1 = [self.table.item(row, 10).text()  # 10 - столбец с коэф. калибровки 1
                              for row in range(self.table.rowCount())
                              if self.table.item(row, 10) is not None]  # 10 - столбец с коэф. калибровки 1

        data_k_calibrate_2 = [self.table.item(row, 11).text()  # 11 - столбец с коэф. калибровки 2
                              for row in range(self.table.rowCount())
                              if self.table.item(row, 11) is not None]  # 11 - столбец с коэф. калибровки 2
        temp = [self.table.item(row, 13).text()  # 13 - столбец с коэф. калибровки 2
                for row in range(self.table.rowCount())
                if self.table.item(row, 13) is not None]  # 13 - столбец с коэф. калибровки 2

        # Здесь уже по-человечески переложить данные и записать в таблицу
        list_voltages = []
        for i in range(0, self.table.rowCount(), 32):
            list_voltages.append(data_voltage[i])

        list_ch_1_k_1 = []
        for i in range(0, self.table.rowCount(), 32):
            list_ch_1_k_1.append(data_k_calibrate_1[i])

        list_ch_1_k_2 = []
        for i in range(0, self.table.rowCount(), 32):
            list_ch_1_k_2.append(data_k_calibrate_2[i])

        list_ch_2_k_1 = []
        for i in range(1, self.table.rowCount(), 32):
            list_ch_2_k_1.append(data_k_calibrate_1[i])

        list_ch_2_k_2 = []
        for i in range(1, self.table.rowCount(), 32):
            list_ch_2_k_2.append(data_k_calibrate_2[i])

        list_ch_3_k_1 = []
        for i in range(2, self.table.rowCount(), 32):
            list_ch_3_k_1.append(data_k_calibrate_1[i])

        list_ch_3_k_2 = []
        for i in range(2, self.table.rowCount(), 32):
            list_ch_3_k_2.append(data_k_calibrate_2[i])

        list_ch_4_k_1 = []
        for i in range(3, self.table.rowCount(), 32):
            list_ch_4_k_1.append(data_k_calibrate_1[i])

        list_ch_4_k_2 = []
        for i in range(3, self.table.rowCount(), 32):
            list_ch_4_k_2.append(data_k_calibrate_2[i])

        list_ch_5_k_1 = []
        for i in range(4, self.table.rowCount(), 32):
            list_ch_5_k_1.append(data_k_calibrate_1[i])

        list_ch_5_k_2 = []
        for i in range(4, self.table.rowCount(), 32):
            list_ch_5_k_2.append(data_k_calibrate_2[i])

        list_ch_6_k_1 = []
        for i in range(5, self.table.rowCount(), 32):
            list_ch_6_k_1.append(data_k_calibrate_1[i])

        list_ch_6_k_2 = []
        for i in range(5, self.table.rowCount(), 32):
            list_ch_6_k_2.append(data_k_calibrate_2[i])

        list_ch_7_k_1 = []
        for i in range(6, self.table.rowCount(), 32):
            list_ch_7_k_1.append(data_k_calibrate_1[i])

        list_ch_7_k_2 = []
        for i in range(6, self.table.rowCount(), 32):
            list_ch_7_k_2.append(data_k_calibrate_2[i])

        list_ch_8_k_1 = []
        for i in range(7, self.table.rowCount(), 32):
            list_ch_8_k_1.append(data_k_calibrate_1[i])

        list_ch_8_k_2 = []
        for i in range(7, self.table.rowCount(), 32):
            list_ch_8_k_2.append(data_k_calibrate_2[i])

        list_ch_9_k_1 = []
        for i in range(8, self.table.rowCount(), 32):
            list_ch_9_k_1.append(data_k_calibrate_1[i])

        list_ch_9_k_2 = []
        for i in range(8, self.table.rowCount(), 32):
            list_ch_9_k_2.append(data_k_calibrate_2[i])

        list_ch_10_k_1 = []
        for i in range(9, self.table.rowCount(), 32):
            list_ch_10_k_1.append(data_k_calibrate_1[i])

        list_ch_10_k_2 = []
        for i in range(9, self.table.rowCount(), 32):
            list_ch_10_k_2.append(data_k_calibrate_2[i])

        list_ch_11_k_1 = []
        for i in range(10, self.table.rowCount(), 32):
            list_ch_11_k_1.append(data_k_calibrate_1[i])

        list_ch_11_k_2 = []
        for i in range(10, self.table.rowCount(), 32):
            list_ch_11_k_2.append(data_k_calibrate_2[i])

        list_ch_12_k_1 = []
        for i in range(11, self.table.rowCount(), 32):
            list_ch_12_k_1.append(data_k_calibrate_1[i])

        list_ch_12_k_2 = []
        for i in range(11, self.table.rowCount(), 32):
            list_ch_12_k_2.append(data_k_calibrate_2[i])

        list_ch_13_k_1 = []
        for i in range(12, self.table.rowCount(), 32):
            list_ch_13_k_1.append(data_k_calibrate_1[i])

        list_ch_13_k_2 = []
        for i in range(12, self.table.rowCount(), 32):
            list_ch_13_k_2.append(data_k_calibrate_2[i])

        list_ch_14_k_1 = []
        for i in range(13, self.table.rowCount(), 32):
            list_ch_14_k_1.append(data_k_calibrate_1[i])

        list_ch_14_k_2 = []
        for i in range(13, self.table.rowCount(), 32):
            list_ch_14_k_2.append(data_k_calibrate_2[i])

        list_ch_15_k_1 = []
        for i in range(14, self.table.rowCount(), 32):
            list_ch_15_k_1.append(data_k_calibrate_1[i])

        list_ch_15_k_2 = []
        for i in range(14, self.table.rowCount(), 32):
            list_ch_15_k_2.append(data_k_calibrate_2[i])

        list_ch_16_k_1 = []
        for i in range(15, self.table.rowCount(), 32):
            list_ch_16_k_1.append(data_k_calibrate_1[i])

        list_ch_16_k_2 = []
        for i in range(15, self.table.rowCount(), 32):
            list_ch_16_k_2.append(data_k_calibrate_2[i])

        list_ch_17_k_1 = []
        for i in range(16, self.table.rowCount(), 32):
            list_ch_17_k_1.append(data_k_calibrate_1[i])

        list_ch_17_k_2 = []
        for i in range(16, self.table.rowCount(), 32):
            list_ch_17_k_2.append(data_k_calibrate_2[i])

        list_ch_18_k_1 = []
        for i in range(17, self.table.rowCount(), 32):
            list_ch_18_k_1.append(data_k_calibrate_1[i])

        list_ch_18_k_2 = []
        for i in range(17, self.table.rowCount(), 32):
            list_ch_18_k_2.append(data_k_calibrate_2[i])

        list_ch_19_k_1 = []
        for i in range(18, self.table.rowCount(), 32):
            list_ch_19_k_1.append(data_k_calibrate_1[i])

        list_ch_19_k_2 = []
        for i in range(18, self.table.rowCount(), 32):
            list_ch_19_k_2.append(data_k_calibrate_2[i])

        list_ch_20_k_1 = []
        for i in range(19, self.table.rowCount(), 32):
            list_ch_20_k_1.append(data_k_calibrate_1[i])

        list_ch_20_k_2 = []
        for i in range(19, self.table.rowCount(), 32):
            list_ch_20_k_2.append(data_k_calibrate_2[i])

        list_ch_21_k_1 = []
        for i in range(20, self.table.rowCount(), 32):
            list_ch_21_k_1.append(data_k_calibrate_1[i])

        list_ch_21_k_2 = []
        for i in range(20, self.table.rowCount(), 32):
            list_ch_21_k_2.append(data_k_calibrate_2[i])

        list_ch_22_k_1 = []
        for i in range(21, self.table.rowCount(), 32):
            list_ch_22_k_1.append(data_k_calibrate_1[i])

        list_ch_22_k_2 = []
        for i in range(21, self.table.rowCount(), 32):
            list_ch_22_k_2.append(data_k_calibrate_2[i])

        list_ch_23_k_1 = []
        for i in range(22, self.table.rowCount(), 32):
            list_ch_23_k_1.append(data_k_calibrate_1[i])

        list_ch_23_k_2 = []
        for i in range(22, self.table.rowCount(), 32):
            list_ch_23_k_2.append(data_k_calibrate_2[i])

        list_ch_24_k_1 = []
        for i in range(23, self.table.rowCount(), 32):
            list_ch_24_k_1.append(data_k_calibrate_1[i])

        list_ch_24_k_2 = []
        for i in range(23, self.table.rowCount(), 32):
            list_ch_24_k_2.append(data_k_calibrate_2[i])

        list_ch_25_k_1 = []
        for i in range(24, self.table.rowCount(), 32):
            list_ch_25_k_1.append(data_k_calibrate_1[i])

        list_ch_25_k_2 = []
        for i in range(24, self.table.rowCount(), 32):
            list_ch_25_k_2.append(data_k_calibrate_2[i])

        list_ch_26_k_1 = []
        for i in range(25, self.table.rowCount(), 32):
            list_ch_26_k_1.append(data_k_calibrate_1[i])

        list_ch_26_k_2 = []
        for i in range(25, self.table.rowCount(), 32):
            list_ch_26_k_2.append(data_k_calibrate_2[i])

        list_ch_27_k_1 = []
        for i in range(26, self.table.rowCount(), 32):
            list_ch_27_k_1.append(data_k_calibrate_1[i])

        list_ch_27_k_2 = []
        for i in range(26, self.table.rowCount(), 32):
            list_ch_27_k_2.append(data_k_calibrate_2[i])

        list_ch_28_k_1 = []
        for i in range(27, self.table.rowCount(), 32):
            list_ch_28_k_1.append(data_k_calibrate_1[i])

        list_ch_28_k_2 = []
        for i in range(27, self.table.rowCount(), 32):
            list_ch_28_k_2.append(data_k_calibrate_2[i])

        list_ch_29_k_1 = []
        for i in range(28, self.table.rowCount(), 32):
            list_ch_29_k_1.append(data_k_calibrate_1[i])

        list_ch_29_k_2 = []
        for i in range(28, self.table.rowCount(), 32):
            list_ch_29_k_2.append(data_k_calibrate_2[i])

        list_ch_30_k_1 = []
        for i in range(29, self.table.rowCount(), 32):
            list_ch_30_k_1.append(data_k_calibrate_1[i])

        list_ch_30_k_2 = []
        for i in range(29, self.table.rowCount(), 32):
            list_ch_30_k_2.append(data_k_calibrate_2[i])

        list_ch_31_k_1 = []
        for i in range(30, self.table.rowCount(), 32):
            list_ch_31_k_1.append(data_k_calibrate_1[i])

        list_ch_31_k_2 = []
        for i in range(30, self.table.rowCount(), 32):
            list_ch_31_k_2.append(data_k_calibrate_2[i])

        list_ch_32_k_1 = []
        for i in range(31, self.table.rowCount(), 32):
            list_ch_32_k_1.append(data_k_calibrate_1[i])

        list_ch_32_k_2 = []
        for i in range(31, self.table.rowCount(), 32):
            list_ch_32_k_2.append(data_k_calibrate_2[i])

        list_temp = []
        for i in range(31, self.table.rowCount(), 32):
            list_temp.append(temp[i])

        table = {'Voltage': list_voltages,
                 'Ch_1_k_1': list_ch_1_k_1, 'Ch_1_k_2': list_ch_1_k_2,
                 'Ch_2_k_1': list_ch_2_k_1, 'Ch_2_k_2': list_ch_2_k_2,
                 'Ch_3_k_1': list_ch_3_k_1, 'Ch_3_k_2': list_ch_3_k_2,
                 'Ch_4_k_1': list_ch_4_k_1, 'Ch_4_k_2': list_ch_4_k_2,
                 'Ch_5_k_1': list_ch_5_k_1, 'Ch_5_k_2': list_ch_5_k_2,
                 'Ch_6_k_1': list_ch_6_k_1, 'Ch_6_k_2': list_ch_6_k_2,
                 'Ch_7_k_1': list_ch_7_k_1, 'Ch_7_k_2': list_ch_7_k_2,
                 'Ch_8_k_1': list_ch_8_k_1, 'Ch_8_k_2': list_ch_8_k_2,
                 'Ch_9_k_1': list_ch_9_k_1, 'Ch_9_k_2': list_ch_9_k_2,
                 'Ch_10_k_1': list_ch_10_k_1, 'Ch_10_k_2': list_ch_10_k_2,
                 'Ch_11_k_1': list_ch_11_k_1, 'Ch_11_k_2': list_ch_11_k_2,
                 'Ch_12_k_1': list_ch_12_k_1, 'Ch_12_k_2': list_ch_12_k_2,
                 'Ch_13_k_1': list_ch_13_k_1, 'Ch_13_k_2': list_ch_13_k_2,
                 'Ch_14_k_1': list_ch_14_k_1, 'Ch_14_k_2': list_ch_14_k_2,
                 'Ch_15_k_1': list_ch_15_k_1, 'Ch_15_k_2': list_ch_15_k_2,
                 'Ch_16_k_1': list_ch_16_k_1, 'Ch_16_k_2': list_ch_16_k_2,
                 'Ch_17_k_1': list_ch_17_k_1, 'Ch_17_k_2': list_ch_17_k_2,
                 'Ch_18_k_1': list_ch_18_k_1, 'Ch_18_k_2': list_ch_18_k_2,
                 'Ch_19_k_1': list_ch_19_k_1, 'Ch_19_k_2': list_ch_19_k_2,
                 'Ch_20_k_1': list_ch_20_k_1, 'Ch_20_k_2': list_ch_20_k_2,
                 'Ch_21_k_1': list_ch_21_k_1, 'Ch_21_k_2': list_ch_21_k_2,
                 'Ch_22_k_1': list_ch_22_k_1, 'Ch_22_k_2': list_ch_22_k_2,
                 'Ch_23_k_1': list_ch_23_k_1, 'Ch_23_k_2': list_ch_23_k_2,
                 'Ch_24_k_1': list_ch_24_k_1, 'Ch_24_k_2': list_ch_24_k_2,
                 'Ch_25_k_1': list_ch_25_k_1, 'Ch_25_k_2': list_ch_25_k_2,
                 'Ch_26_k_1': list_ch_26_k_1, 'Ch_26_k_2': list_ch_26_k_2,
                 'Ch_27_k_1': list_ch_27_k_1, 'Ch_27_k_2': list_ch_27_k_2,
                 'Ch_28_k_1': list_ch_28_k_1, 'Ch_28_k_2': list_ch_28_k_2,
                 'Ch_29_k_1': list_ch_29_k_1, 'Ch_29_k_2': list_ch_29_k_2,
                 'Ch_30_k_1': list_ch_30_k_1, 'Ch_30_k_2': list_ch_30_k_2,
                 'Ch_31_k_1': list_ch_31_k_1, 'Ch_31_k_2': list_ch_31_k_2,
                 'Ch_32_k_1': list_ch_32_k_1, 'Ch_32_k_2': list_ch_32_k_2,
                 'Temp': list_temp,
                 }
        df = pd.DataFrame(table)
        # create excel writer
        writer = pd.ExcelWriter('table_for_grafics.xlsx')
        # write dataframe to excel sheet named 'marks'
        df.to_excel(writer, 'Sheet1')
        # save the excel file
        writer.save()


class SetVoltageRegulatorWindow(QtWidgets.QDialog):

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.resize(300, 300)

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
        VoltageRegulator.port = port  # Задать порт из формы
        VoltageRegulator.speed = speed  # Задать скорость из формы
        self.close()


class SearchThread(QtCore.QThread):
    thread_signal = QtCore.pyqtSignal(int)
    thread_data = QtCore.pyqtSignal(list, int, int, str)
    count_voltage_step = 8  # так как 8 напряжений калибровки калибровки
    count_channel_calibrate = 32  # Вернуть 32.
    count_bytes_in_one_channel = 16

    def __init__(self, parent=None):
        # self.running = False  # Флаг выполнения
        QtCore.QThread.__init__(self, parent)

    def run(self):
        compare_level = CompareLevel()
        voltages = MeasurementErrorWindow.voltages  # Получить напряжение из формы

        voltage_regulator = VoltageRegulator()  # Создать объект Regulator
        voltage_regulator.set_port()  # Задать порт
        voltage_regulator.power_em()  # Подать питание
        i = 0
        flag_dac_1 = False
        flag_dac_2 = False
        flag_search_compare = False

        # Здесь запросим коэффициенты полинома
        write = read_k_polinoms()  # Чтение коэффициентов полиномов
        Ethernet().swap(write)
        write = data_request(0)  # Запрос данных (калибровочных коэффициентов)
        data = Ethernet().swap(write)
        # 8 байт - Frame, 24 байта - любых см. команду write_k_polinoms()
        undefined_bytes = 24  # Было 24 - решил убрать для экономии памяти
        k_polinoms = data[1][22 + 8 + undefined_bytes:]
        k_polinoms = k_polinoms[0:self.count_channel_calibrate * self.count_bytes_in_one_channel]
        list_polinoms = []
        list_error = []
        # Переложим коэффициенты k_polinoms в список списков для удобства работы
        for i in range(0, self.count_channel_calibrate):
            row_polinoms = []
            for j in range(0, self.count_bytes_in_one_channel):
                row_polinoms.append(k_polinoms[i * self.count_bytes_in_one_channel + j])
            list_polinoms.append(row_polinoms)
        for voltage in voltages:
            voltage_regulator.set_calibrate_voltage(float(voltage))  # Управлять входным напряжением
            for channel in range(0, self.count_channel_calibrate):
                error = MeasurementErrorWindow.error  # Получить начальную ошибку из формы
                # Вычислить откалиброванное напряжение
                # list_polinoms.append(voltage)
                args = list_polinoms[channel]
                y = (int.from_bytes([args[1], args[0]], byteorder='big') / (10 ** 8)) * (float(voltage) ** 3) + \
                    (int.from_bytes([args[3], args[2]], byteorder='big') / (10 ** 6)) * (float(voltage) ** 2) + \
                    (int.from_bytes([args[5], args[4]], byteorder='big') / (10 ** 5)) * float(voltage) + \
                    (int.from_bytes([args[7], args[6]], byteorder='big') / (10 ** 3))
                voltage_calibrate = float(format(float(voltage) / y, '.2f'))

                # Пока флаг не найден
                while (flag_search_compare == False) or (error >= 0):
                    voltage_down = round(voltage_calibrate - ((voltage_calibrate * error) / 100), 2)
                    voltage_up = round(voltage_calibrate + ((voltage_calibrate * error) / 100), 2)
                    levels = {str(channel + 1): [voltage_down, voltage_up]}
                    logs = compare_level.compare_level(0, **levels)
                    log_1 = logs[0]
                    log_2 = logs[1]
                    log_r_1 = []
                    log_r_2 = []
                    for i in log_1:
                        log_r_1.append(i)
                    log_r_1.reverse()
                    log_1_int = int.from_bytes(bytes(log_r_1), byteorder='big')
                    for i in log_2:
                        log_r_2.append(i)
                    log_r_2.reverse()
                    log_2_int = int.from_bytes(bytes(log_r_2), byteorder='big')

                    # Маска контролируемых каналов побитово
                    int_mask_channels = round(2 ** channel)

                    # Накладывать log_1_int и log_2_int на int_mask_channels
                    # Если после наложения log_1_int != int_mask_channels - значит переключился
                    mask_1 = log_1_int & int_mask_channels
                    mask_2 = log_2_int & int_mask_channels
                    if (mask_1 != int_mask_channels) and (mask_2 != int_mask_channels):
                        flag_search_compare = True  # Погрешность найдена
                        list_error.append(error)
                    error -= 1.0  # Уменьшаем погрешности (шаг)

                i += 1
                self.thread_signal.emit(i)  # Для прогрессбара
        voltage_regulator.power(0)  # Выключить питание после выполнения калибровки

    @staticmethod
    def calculate_k_polinoms(*args, voltage):
        print(voltage)
        y = ((float(args[0]) / (10 ** 8)) * float(args[-1]) ** 3) + \
            ((float(args[1]) / (10 ** 6)) * float(args[-1]) ** 2) + \
            ((float(args[2]) / (10 ** 5)) * float(args[-1])) + \
            float(args[3])
        rez = args[-1] / y
        return format(rez, '.2f')


class MeasurementErrorWindow(QtWidgets.QWidget):
    voltages = [0, 0, 0, 0, 0, 0, 0, 0]
    error = 0

    def __init__(self, parent=None):
        super().__init__(parent)
        # self.resize(600, 100)
        self.counter = 0
        self.layout = QGridLayout()  # Создание сетки - Основная

        # Блок нулевой
        self.nullblock = QtWidgets.QHBoxLayout()  # Создаем горизонтальный контейнер 1
        self.addr_IP = QtWidgets.QLabel('IP адрес устройства')
        self.addr_IP.setFont(QtGui.QFont("Times", 10))
        self.addr_IP.setFixedWidth(150)
        self.add_addr_IP = QtWidgets.QLineEdit()
        self.add_addr_IP.setFixedWidth(115)
        # self.add_addr_IP.setInputMask('DDD.999.999.999;#') # Убрать!
        self.add_addr_IP.setText('192.168.1.0')
        self.port_IP = QtWidgets.QLabel('Номер порта')
        self.port_IP.setFont(QtGui.QFont("Times", 10))
        self.port_IP.setFixedWidth(150)
        # self.port_IP.setContentsMargins(10, 0, 0, 0)
        self.add_port_IP = QtWidgets.QLineEdit()
        # self.port_IP.setContentsMargins(20,0,0,0)
        self.add_port_IP.setFixedWidth(50)
        self.add_port_IP.setInputMask('DDDD')
        self.add_port_IP.setText('1233')

        # Формирование интерфейса нулевого блока
        self.nullblock.addWidget(self.addr_IP, Qt.AlignJustify)
        self.nullblock.addWidget(self.add_addr_IP, Qt.AlignJustify)
        self.nullblock.addWidget(self.port_IP, Qt.AlignJustify)
        self.nullblock.addWidget(self.add_port_IP, Qt.AlignJustify)
        self.nullblock.addStretch()
        self.layout.addLayout(self.nullblock, 0, 0)
        self.layout.addWidget(QHLine(), 1, 0)  # ГОРИЗОНТАЛЬНЫЙ РАЗДЕЛИТЕЛЬ

        # Блок первый
        self.layout.addWidget(self.channels_group(), 2, 0)
        self.layout.addWidget(self.error_group(), 2, 1)
        self.setWindowTitle('Оценка погрешностей')

        # Блок второй
        self.twoblock = QtWidgets.QHBoxLayout()  # Создаем горизонтальный контейнер 1
        self.button_comport = QtWidgets.QPushButton("Настройка COM-порта")
        self.button_comport.setFont(QtGui.QFont("Times", 10))
        self.button_comport.setFixedWidth(200)
        self.button_run_search_error = QtWidgets.QPushButton("Начать оценку")
        self.button_run_search_error.setFont(QtGui.QFont("Times", 10))
        self.button_run_search_error.setFixedWidth(200)

        # Формирование интерфейса второго блока
        self.twoblock.addWidget(self.button_comport, Qt.AlignCenter)
        self.twoblock.addWidget(self.button_run_search_error, Qt.AlignCenter)
        self.button_comport.clicked.connect(self.setting_port)
        self.button_run_search_error.clicked.connect(self.run_thread)

        # self.twoblock.addStretch(100)
        self.layout.addLayout(self.twoblock, 3, 0)

        # Третий блок с таблицей
        self.threeblock = QtWidgets.QHBoxLayout()
        self.table = QTableWidget(256, 7)
        self.vbox = QtWidgets.QVBoxLayout()

        self.button_export = QtWidgets.QPushButton("Экспорт в *.xlsx")
        self.button_export.setFont(QtGui.QFont("Times", 10))
        self.button_export.setFixedWidth(200)
        self.button_export.clicked.connect(self.export_calibrate)
        self.button_export.setEnabled(False)  # Заблокировать кнопку

        # self.button_write_k_calibrate = QtWidgets.QPushButton("Записать коэффициенты в ПЗУ")
        # self.button_write_k_calibrate.setFont(QtGui.QFont("Times", 10))
        # self.button_write_k_calibrate.setFixedWidth(200)
        # self.button_write_k_calibrate.clicked.connect(self.write_k_calibrate)
        # self.button_write_k_calibrate.setEnabled(False)  # Заблокировать кнопку

        self.button_graf = QtWidgets.QPushButton("Показать график")
        self.button_graf.setFont(QtGui.QFont("Times", 10))
        self.button_graf.setFixedWidth(200)
        self.button_graf.clicked.connect(self.graf_calibrate)
        self.button_graf.setEnabled(False)  # Заблокировать кнопку

        # self.vbox.addWidget(self.button_write_k_calibrate)
        self.vbox.addWidget(self.button_export)
        self.vbox.addWidget(self.button_graf)
        self.vbox.addStretch()  # Пружина

        # Set the table headers
        self.table.setHorizontalHeaderLabels(["N", "Channel", "Voltage", "Code_1", "Code_2", "Avg_Code", "Error"])

        # self.table.resizeColumnsToContents()
        self.threeblock.addWidget(self.table)
        self.layout.addLayout(self.threeblock, 4, 0)
        self.layout.addLayout(self.vbox, 4, 1)

        # Ниже описание и настройка потока для работы с ЭМ1
        self.automatic_search_thread = SearchThread()  # Содаем экземпляр класса StageThread
        self.automatic_search_thread.started.connect(self.on_started)
        self.automatic_search_thread.thread_signal.connect(self.on_change, QtCore.Qt.QueuedConnection)
        self.automatic_search_thread.thread_data.connect(self.table_update, QtCore.Qt.QueuedConnection)
        self.automatic_search_thread.finished.connect(self.on_finished)

        # sub.setWidget(self.setLayout(self.layout))

        # Пятый блок
        # Ниже создан прогресс бар
        self.fourblock = QtWidgets.QHBoxLayout()
        self.progress_bar = QtWidgets.QProgressBar()
        count = CalibrateThread.count_channel_calibrate * CalibrateThread.count_voltage_step
        self.progress_bar.setRange(0, count)
        self.fourblock.addWidget(self.progress_bar)
        self.layout.addLayout(self.fourblock, 5, 0)

        # Вывод содержимого сетки на экран
        self.setLayout(self.layout)

    def channels_group(self):
        groupBox = QGroupBox("Задайте уровни для оценки от наименьшего к наибольшему")
        groupBox.setFont(QtGui.QFont("Times", 10))
        # groupBox.resize(600,100)
        self.voltage_1_label = QtWidgets.QLabel('1 уровень,(В)')
        self.voltage_1 = QtWidgets.QLineEdit()
        self.voltage_1.setText('2')
        # self.voltage_1.setFixedWidth(30)

        self.voltage_2_label = QtWidgets.QLabel('2 уровень,(В)')
        self.voltage_2 = QtWidgets.QLineEdit()
        # self.voltage_2.setFixedWidth(30)
        self.voltage_2.setText('6')

        self.voltage_3_label = QtWidgets.QLabel('3 уровень,(В)')
        self.voltage_3 = QtWidgets.QLineEdit()
        # self.voltage_3.setFixedWidth(30)
        self.voltage_3.setText('10')

        self.voltage_4_label = QtWidgets.QLabel('4 уровень,(В)')
        self.voltage_4 = QtWidgets.QLineEdit()
        # self.voltage_4.setFixedWidth(30)
        self.voltage_4.setText('14')

        self.voltage_5_label = QtWidgets.QLabel('5 уровень,(В)')
        self.voltage_5 = QtWidgets.QLineEdit()
        # self.voltage_5.setFixedWidth(30)
        self.voltage_5.setText('18')

        self.voltage_6_label = QtWidgets.QLabel('6 уровень,(В)')
        self.voltage_6 = QtWidgets.QLineEdit()
        # self.voltage_6.setFixedWidth(30)
        self.voltage_6.setText('22')

        self.voltage_7_label = QtWidgets.QLabel('7 уровень,(В)')
        self.voltage_7 = QtWidgets.QLineEdit()
        # self.voltage_7.setFixedWidth(30)
        self.voltage_7.setText('26')

        self.voltage_8_label = QtWidgets.QLabel('8 уровень,(В)')
        self.voltage_8 = QtWidgets.QLineEdit()
        # self.voltage_8.setFixedWidth(30)
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

    def error_group(self):
        groupBox = QGroupBox("Задайте погрешность")
        groupBox.setFont(QtGui.QFont("Times", 10))
        groupBox.setFixedWidth(200)
        self.error_label = QtWidgets.QLabel('Начальная погрешность, %')
        self.error = QtWidgets.QLineEdit()
        self.error.setText('25')
        self.error.setFixedWidth(50)
        vbox_1 = QtWidgets.QVBoxLayout()
        vbox_1.addWidget(self.error_label)
        vbox_1.addWidget(self.error)
        groupBox.setLayout(vbox_1)
        return groupBox

    def setting_port(self):
        addr_IP = self.add_addr_IP.text()  # Получить введенное значение в поле
        port_IP = self.add_port_IP.text()  # Получить введенное значение в поле

        # Установка addr и port
        Ethernet.port = int(port_IP)
        Ethernet.host = str(addr_IP)

        MeasurementErrorWindow.error = int(self.error.text())
        volt_1 = self.voltage_1.text()
        volt_2 = self.voltage_2.text()
        volt_3 = self.voltage_3.text()
        volt_4 = self.voltage_4.text()
        volt_5 = self.voltage_5.text()
        volt_6 = self.voltage_6.text()
        volt_7 = self.voltage_7.text()
        volt_8 = self.voltage_8.text()

        MeasurementErrorWindow.voltages = [volt_1, volt_2, volt_3, volt_4, volt_5, volt_6, volt_7, volt_8]
        if self.error == '':
            msg_box = QMessageBox(QtWidgets.QMessageBox.Warning,
                                  "Внимание!",
                                  "Пожалуйста заполните полe напряжений",
                                  buttons=QtWidgets.QMessageBox.Close,
                                  parent=None
                                  )
            msg_box.exec_()
        # Задание COM порта
        com_port = GwINSTEKWindow(self)
        com_port.setWindowTitle('COM')
        com_port.exec_()

    def on_started(self):  # Запускается в начале потока
        self.start_time = datetime.datetime.now()

    def on_finished(self):  # Запускается после окончания выполнения потока просто для наглядности
        msg_box = QMessageBox(QtWidgets.QMessageBox.Information,
                              "Оценка погрешности окончена!",
                              "Время оценки: {} ".format((datetime.datetime.now() - self.start_time)),
                              buttons=QtWidgets.QMessageBox.Close,
                              parent=None
                              )
        msg_box.exec_()
        self.return_table()
        self.button_export.setEnabled(True)  # Разблокировать кнопку
        self.button_graf.setEnabled(True)  # Разблокировать кнопку
        # self.button_write_k_calibrate.setEnabled(True)  # Разблокировать кнопку
        # self.automatic_calibrate_thread.yieldCurrentThread()  # Принудительное завершение потока

    def on_change(self, i):  # Принимаем число из потока в Progressbar
        self.progress_bar.setValue(i)

    def run_thread(self):
        if not self.automatic_search_thread.isRunning():
            self.automatic_search_thread.start()  # Запускаем поток

    def table_update(self, data, number, vector, voltage):
        self.channel = int(number)
        self.table.setItem((32 * self.counter) + number, 0, QTableWidgetItem(str((32 * self.counter) + number)))
        self.table.setItem((32 * self.counter) + number, 1, QTableWidgetItem(str(self.channel + 1)))
        self.table.setItem((32 * self.counter) + number, 2, QTableWidgetItem(str(voltage)))
        self.table.setItem((32 * self.counter) + number, 3, QTableWidgetItem(str(vector)))
        self.table.setItem((32 * self.counter) + number, 4, QTableWidgetItem(str(int(data[2]))))
        self.table.setItem((32 * self.counter) + number, 5, QTableWidgetItem(str(int(data[3]))))
        average_code = (data[2] + data[3]) / 2
        self.table.setItem((32 * self.counter) + number, 6, QTableWidgetItem(str(average_code)))
        try:
            k_calibrate = (float(voltage) / 11.05) / ((3.3 * round(average_code)) / 4095)
        except ZeroDivisionError:
            k_calibrate = 0
        self.table.setItem((32 * self.counter) + number, 7, QTableWidgetItem(format(k_calibrate, '.2f')))
        if number == 31:
            self.counter += 1

    def closeEvent(self, event):
        self.hide()  # Скрываем окно
        self.automatic_search_thread.wait(2000)  # Время чтобы закончить
        event.accept()  # Закрываем окно

    def export_calibrate(self):
        exportToExcel(self)

    def graf_calibrate(self):
        grafic_window = GraficWindow()
        grafic_window.show()
        grafic_window.exec_()  # Не знаю как, но это работает

    # @staticmethod
    # def split_list(arr, size):
    #     arrs = []
    #     while len(arr) > size:
    #         pice = arr[:size]
    #         arrs.append(pice)
    #         arr = arr[size:]
    #     arrs.append(arr)
    #     return arrs

    def return_table(self):
        data_voltage = [self.table.item(row, 2).text()  # 2 - столбец с напряжением
                        for row in range(self.table.rowCount())
                        if self.table.item(row, 2) is not None]  # 2 - столбец с напряжением

        data_k_calibrate = [self.table.item(row, 7).text()  # 7 - столбец с коэф. калибровки
                            for row in range(self.table.rowCount())
                            if self.table.item(row, 7) is not None]  # 7 - столбец с коэф. калибровки

        table = {'Voltage': data_voltage, 'K_kalibrate': data_k_calibrate}
        df = pd.DataFrame(table)
        # create excel writer
        writer = pd.ExcelWriter('table_for_grafics.xlsx')
        # write dataframe to excel sheet named 'marks'
        df.to_excel(writer, 'Sheet1')
        # save the excel file
        writer.save()
