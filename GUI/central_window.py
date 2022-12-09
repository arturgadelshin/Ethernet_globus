from PyQt5 import QtCore, QtWidgets, QtGui
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QStandardItem, QBrush, QStandardItemModel
from PyQt5.QtWidgets import QPlainTextEdit, QScrollArea, QGridLayout, QAbstractItemView, QFrame
from GUI.central_window import *
from GwInstek74303S.GUI.GwINSTEK import GwINSTEKWindow
from GwInstek74303S.com_voltage_regulator import *
from stages import Stages_03, Stages_02, Stages_01
from PyQt5 import QtWidgets, QtGui, QtCore
from globus_ethernet import Ethernet
from loggings import *


# voltage_regulator.power_em()  # Включаем питание


class StageThread(QtCore.QThread):
    thread_signal = QtCore.pyqtSignal(int)
    thread_data = QtCore.pyqtSignal(list)
    thread_interface_update = QtCore.pyqtSignal(list, int)
    thread_smk_update = QtCore.pyqtSignal(list, int)
    thread_single_mode_update = QtCore.pyqtSignal(list, int)
    clear_color_in_tree = QtCore.pyqtSignal()

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def run(self):
        # Здесь живёт отдельный поток
        voltage_regulator = VoltageRegulator()
        voltage_regulator.set_port()  # Создаем соединение с портом
        voltage_regulator.power_em()  # Подать питание
        voltage_regulator.port_close()  # Закрыть порт - нужно, чтобы создать новый объект и изменять напряжение
        st_1 = Stages_01()
        st_2 = Stages_02()
        st_3 = Stages_03()
        # Ниже список с параметрами из st_x
        interface_param = CentralWindow.interface_param
        smk_param = CentralWindow.smk_param
        single_mode = CentralWindow.single_mode
        list_interface_param = [st_1.parameter_01, st_1.parameter_02,
                                st_1.parameter_03, st_1.parameter_04]  # Все параметры

        list_smk_param = [st_2.parameter_01, ]

        list_single_mode = [st_3.parameter_01, st_3.parameter_02, st_3.parameter_03]


        list_flag_interface = []  # Кол-во флагов должно быть равно кол-ву параметров
        list_flag_smk = []  # Кол-во флагов должно быть равно кол-ву параметров
        list_flag_single_mode = []  # Кол-во флагов должно быть равно кол-ву параметров

        for i in interface_param:
            if i.checkState() == 0:
                list_flag_interface.append(0)
                continue
            list_flag_interface.append(1)

        for i in smk_param:
            if i.checkState() == 0:
                list_flag_smk.append(0)
                continue
            list_flag_smk.append(1)

        for i in single_mode:
            if i.checkState() == 0:
                list_flag_single_mode.append(0)
                continue
            list_flag_single_mode.append(1)

        # Вычитка буфера перед началом работы с платой не требуется
        # Исходное soft очищает буфер модуля
        # Ниже код для запуска только выделенных параметров!!!

        self.clear_color_in_tree.emit()  # Вызов очистки дерева

        self.signal_count_param = 0
        for i in range(0, (len(list_flag_interface))):
            if list_flag_interface[i] == 1:
                receive_data = list_interface_param[i]()
                self.thread_interface_update.emit(receive_data, i)
                self.thread_data.emit(receive_data)
                #QtCore.QThread.msleep(100)
            self.signal_count_param = i
            self.thread_signal.emit(i)  # Передача через сигнал значения для LoadBar

        for i in range(0, (len(list_flag_smk))):
            if list_flag_smk[i] == 1:
                receive_data = list_smk_param[i]()
                self.thread_smk_update.emit(receive_data, i)
                self.thread_data.emit(receive_data)
                #QtCore.QThread.msleep(100)
            self.thread_signal.emit(i+1+self.signal_count_param)  # Передача через сигнал значения для LoadBar

        for i in range(0, (len(list_flag_single_mode))):
            if list_flag_single_mode[i] == 1:
                receive_data = list_single_mode[i]()
                self.thread_single_mode_update.emit(receive_data, i)

                # QtCore.QThread.msleep(100)
            self.thread_signal.emit(i + 1 + self.signal_count_param)  # Передача через сигнал значения для LoadBar
        voltage_regulator.set_port()  # Создаем соединение с портом
        voltage_regulator.power(0)  # Выключить питание


class CentralWindow(QtWidgets.QWidget):  # Использовать для других окон
    # Ниже список с параметрами из st - экземпляра объекта Stage_01
    interface_param = [QStandardItem(Stages_01().name_param_01), QStandardItem(Stages_01().name_param_02),
                       QStandardItem(Stages_01().name_param_03), QStandardItem(Stages_01().name_param_04)]

    smk_param = [QStandardItem(Stages_02().name_param_01), ]
    single_mode = [QStandardItem(Stages_03().name_param_01), QStandardItem(Stages_03().name_param_02),
                   QStandardItem(Stages_03().name_param_03)]
    # Здесь задаются цвета годе/негоден
    brush_red = QBrush(Qt.red)
    brush_green = QBrush(Qt.green)
    brush_reset_color = QtGui.QColor(255, 255, 255, 0)

    """Central Window"""
    def __init__(self, parent=None):
        super().__init__(parent)
        #sub = QMdiSubWindow()
        self.addr_IP = QtWidgets.QLabel('IP адрес устройства')
        self.add_addr_IP = QtWidgets.QLineEdit()

        self.add_addr_IP.setFixedWidth(115)
        #self.add_addr_IP.setInputMask('DDD.999.999.999;#') # Убрать!
        self.add_addr_IP.setText('192.168.1.0')
        self.port_IP = QtWidgets.QLabel('Номер порта')
        #self.port_IP.setContentsMargins(10, 0, 0, 0)
        self.add_port_IP = QtWidgets.QLineEdit()

        #self.port_IP.setContentsMargins(20,0,0,0)
        self.add_port_IP.setFixedWidth(50)
        self.add_port_IP.setInputMask('DDDD')
        self.add_port_IP.setText('1233')

        self.button_OK = QtWidgets.QPushButton("ПРИМЕНИТЬ")
        self.button_OK.setFixedWidth(100)
        self.button_addition = QtWidgets.QPushButton("Дополнительно")
        self.button_addition.setFixedWidth(100)
        self.button_calibrate = QtWidgets.QPushButton("Калибровка")
        self.button_calibrate.setFixedWidth(100)

        # self.kostil = QtWidgets.QLineEdit()
        # self.kostil.setEnabled(False)

        self.treeView = QtWidgets.QTreeView() # Создаем виджет дерева
        self.log = QPlainTextEdit()  # Создаем текстовое поля для вывода лога
        self.scroll = QScrollArea()  # Создаем скролл в который засунем текстовое поле лога?

        self.layout = QGridLayout()  # Создание сетки  1 - Основная

        # Фомирование первого блока интерфейса
        self.oneblock = QtWidgets.QHBoxLayout()  # Создаем горизонтальный контейнер 1
        self.oneblock.addWidget(self.addr_IP, Qt.AlignLeft)
        self.oneblock.addWidget(self.add_addr_IP, Qt.AlignJustify)
        self.oneblock.addWidget(self.port_IP, Qt.AlignLeft)
        self.oneblock.addWidget(self.add_port_IP, Qt.AlignLeft)
        self.oneblock.addWidget(self.button_OK, Qt.AlignLeft)
        self.oneblock.addWidget(self.button_addition, Qt.AlignLeft)
        self.oneblock.addWidget(self.button_calibrate, Qt.AlignLeft)
        self.button_addition.setEnabled(False)  # Заблокировать кнопку
        self.button_calibrate.setEnabled(False)  # Заблокировать кнопку
        self.button_OK.clicked.connect(self.on_connect)
        self.oneblock.addStretch(100)
        self.layout.addLayout(self.oneblock, 0, 0, 1, 2)


        # Фомирование второго блока интерфейса
        self.twoblock = QtWidgets.QHBoxLayout()  # Создаем горизонтальный контейнер 2

        # Настройка log
        self.log.documentTitle()  # Задаем заголовок документа
        self.log.createStandardContextMenu()  # Стандартное меню по правой клавише
        self.log.setTextInteractionFlags(Qt.TextSelectableByMouse)  # Текст можно только выделить мышью
        self.log.setReadOnly(True)  # Текстовое поле доступно только для чтения
        #self.log.setPlainText("Текст заглушка для проверки окна ЛОГА аглушка для проверки\n"*90) # Загружает текст в окно
        self.log.setMinimumWidth(400)

        # Создаем виджет дерева
        self.treeView = QtWidgets.QTreeView()
        self.treeView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.model = QStandardItemModel()
        self.model.setHorizontalHeaderLabels(['Наименование проверок'])
        #self.treeView.setModel(self.model)
        self.treeView.setUniformRowHeights(True)


        # Добавляем виджеты в сетку 2
        self.twoblock.addWidget(self.treeView,)
        #self.layout.addWidget(self.treeView, 1, 0, Qt.AlignHCenter)
        #self.layout_2.addWidget(self.log, 1, 2, Qt.AlignRight )
        self.twoblock.addWidget(self.log, )
        self.layout.setContentsMargins(10, 10, 10, 10)  # Формирование отступов
        self.layout.addLayout(self.twoblock, 1, 0, 1, 4)

        # Конец формирования второго блока интерфейса



        # Фомирование третьего блока интерфейса
        #self.layout_3 = QGridLayout()  # Создание сетки 3 блока
        self.threeblock = QtWidgets.QHBoxLayout()  # Создаем горизонтальный контейнер 3

        self.button_RUN = QtWidgets.QPushButton("Начать проверку")
        self.button_RUN.setFixedWidth(100)
        self.button_RUN.clicked.connect(self.run_thread)

        self.button_RESET_ALL = QtWidgets.QPushButton("Сброосить всё")
        self.button_RESET_ALL.setFixedWidth(100)
        self.button_RESET_ALL.clicked.connect(self.reset_all)

        self.button_SET_ALL = QtWidgets.QPushButton("Установить всё")
        self.button_SET_ALL.setFixedWidth(100)
        self.button_SET_ALL.clicked.connect(self.set_all)

        # Ниже создан прогресс бар
        self.progress_bar = QtWidgets.QProgressBar()
        self.progress_bar.setRange(0, 4)  # Задал 4 так как 5 параметров пока что, является слотом

        self.button_CLEAR = QtWidgets.QPushButton("Очистить лог")
        self.button_CLEAR.setFixedWidth(100)
        self.button_CLEAR.clicked.connect(self.log_clear)

        self.threeblock.addWidget(self.button_RUN, )
        self.threeblock.addWidget(self.button_RESET_ALL, )
        self.threeblock.addWidget(self.button_SET_ALL, )
        self.threeblock.addWidget(self.progress_bar, )
        self.threeblock.addWidget(self.button_CLEAR, )
        self.layout.addLayout(self.threeblock, 3, 0, 1, 4)

        # Вывод содержимого сетки на экран
        self.setLayout(self.layout)

        # # Вывод содержимого сетки на экран
        # self.setLayout(self.layout)

        # Ниже описание и настройка потока для работы с ЭМ1
        self.stage_thread = StageThread()  # Содаем экземпляр класса StageThread
        #self.stage_thread.started.connect(self.on_started)
        self.stage_thread.finished.connect(self.on_finished)
        self.stage_thread.thread_signal.connect(self.on_change, QtCore.Qt.QueuedConnection)
        self.stage_thread.thread_interface_update.connect(self.tree_interface_update, QtCore.Qt.QueuedConnection)
        self.stage_thread.thread_smk_update.connect(self.tree_smk_update, QtCore.Qt.QueuedConnection)
        self.stage_thread.thread_single_mode_update.connect(self.tree_single_mode_update, QtCore.Qt.QueuedConnection)
        self.stage_thread.thread_data.connect(self.log_update, QtCore.Qt.QueuedConnection)
        self.stage_thread.clear_color_in_tree.connect(self.clear_color, QtCore.Qt.QueuedConnection)
        #sub.setWidget(self.setLayout(self.layout))
        #sub.show()

    def log_clear(self):
        self.log.clear()

    def on_connect(self):
        self.button_OK.setEnabled(False)   # Заблокировать кнопку
        addr_IP = self.add_addr_IP.text()  # Получить введенное значение в поле
        port_IP = self.add_port_IP.text()  # Получить введенное значение в поле

        # Установка addr и port
        Ethernet.port = int(port_IP)
        Ethernet.host = str(addr_IP)

        self.header_stage_01 = QStandardItem(Stages_01().name_stage)
        self.header_stage_02 = QStandardItem(Stages_02().name_stage)
        self.header_stage_03 = QStandardItem(Stages_03().name_stage)
        self.model.appendRow([self.header_stage_01])  # Заголовок вложенной строки
        self.model.appendRow([self.header_stage_02])  # Заголовок вложенной строки
        self.model.appendRow([self.header_stage_03])  # Заголовок вложенной строки

        # Вывод списка всех проверяемых параметров
        # Для интерфейсных параметров
        for i in self.interface_param:
            i.setCheckable(True)  #  Добавление флажка
            i.setCheckState(2)   # Задание по умолчанию флаг активен
            self.header_stage_01.appendRow(i)  # Вывод строк для дерева списка
        # Для самоконтроля
        for i in self.smk_param:
            i.setCheckable(True)  # Добавление флажка
            i.setCheckState(2)  # Задание по умолчанию флаг активен
            self.header_stage_02.appendRow(i)  # Вывод строк для дерева списка
        # Для одиночного режима
        for i in self.single_mode:
            i.setCheckable(True)  # Добавление флажка
            i.setCheckState(2)  # Задание по умолчанию флаг активен
            self.header_stage_03.appendRow(i)  # Вывод строк для дерева списка


        self.button_addition.setEnabled(True)  # Раблокировать кнопку
        self.button_calibrate.setEnabled(True)  # Раблокировать кнопку
        self.button_calibrate.clicked.connect(self.calibrate)

        self.treeView.setModel(self.model)  # Вывод дерева списка
        self.treeView.setColumnWidth(0, 350)  # Задать ширину 1 столбца
        self.treeView.expandAll()  # Отобразить все дочерние элементы раскрыть дерево

        clear_log_file()  # Очистка текстового лога

    def on_started(self):  # Запускается в начале потока
        ...

    def on_finished(self): # Запускается после окончания выполнения потока просто для наглядности
        #self.button_OK.setEnabled(True) # Разблокировать кнопку
        self.stage_thread.yieldCurrentThread()  # Принудительное завершение потока

    def on_change(self, i): # Принимаем число из потока в Progressbar
        #self.log.setTextCursor(i[0])

        #self.stage_thread.thread_receive_data.connect(self.updatelog)
        self.progress_bar.setValue(i)


    def tree_interface_update(self, text, iter):  # Функция, которая обновляет в потоке цвет параметра
        interface_param = CentralWindow.interface_param
        if interface_param[iter].checkState() == 2:
            if text[2] == True:
                interface_param[iter].setBackground(self.brush_green)
            else:
                interface_param[iter].setBackground(self.brush_red)

    def tree_smk_update(self, text, iter):  # Функция, которая обновляет в потоке цвет параметра
        smk_param = CentralWindow.smk_param
        if smk_param[iter].checkState() == 2:
            if text[2] == True:
                smk_param[iter].setBackground(self.brush_green)
            else:
                smk_param[iter].setBackground(self.brush_red)

    def tree_single_mode_update(self, text, iter):  # Функция, которая обновляет в потоке цвет параметра
        single_mode = CentralWindow.single_mode
        if single_mode[iter].checkState() == 2:
            if text[1] == True:
                single_mode[iter].setBackground(self.brush_green)
            else:
                single_mode[iter].setBackground(self.brush_red)

    def clear_color(self):  # Функция очистки дерева от цветов годен/негоден
        interface_param = CentralWindow.interface_param
        smk_param = CentralWindow.smk_param
        single_mode = CentralWindow.single_mode
        for i in interface_param:
            i.setBackground(self.brush_reset_color)
        for i in smk_param:
            i.setBackground(self.brush_reset_color)
        for i in single_mode:
            i.setBackground(self.brush_reset_color)


    def log_update(self, text):
        text_read = f'READ-'\
                    f'UID: {text[0][1][0:2]},' \
                    f'GED_S: {text[0][1][2:4]},' \
                    f'HEAD: {text[0][1][4:8]},' \
                    f'TAIL: {text[0][1][8:12]},' \
                    f'LEN_C: {text[0][1][12:14]},' \
                    f'MARK_T: {text[0][1][14]}' \
                    f'TIME: {text[0][1][15:20]},' \
                    f'CODE_C: {text[0][1][20]}' \
                    f'ST_C: {text[0][1][21]}' \
                    f'DATA: {text[0][1][22:]}' \
            #print(text_read)
        self.log.appendPlainText(text_read)

    def run_thread(self):
        if GwINSTEKWindow.flag_setting == 0:  # Чтобы второй раз при повторе не выбирать COM
            # Задание COM порта
            com_port = GwINSTEKWindow(self)
            com_port.setWindowTitle('COM')
            com_port.exec_()
        self.stage_thread.start()  # Запускаем поток

    def reset_all(self):
        for i in self.interface_param:
            i.setCheckState(0)   # Задание по умолчанию флаг неактивен

        for i in self.smk_param:
            i.setCheckState(0)   # Задание по умолчанию флаг неактивен

        for i in self.single_mode:
            i.setCheckState(0)  # Задание по умолчанию флаг неактивен

    def set_all(self):
        for i in self.interface_param:
            i.setCheckState(2)   # Задание по умолчанию флаг активен

        for i in self.smk_param:
            i.setCheckState(2)  # Задание по умолчанию флаг неактивен

        for i in self.single_mode:
            i.setCheckState(2)  # Задание по умолчанию флаг неактивен

    def calibrate(self):
        pass


class QHLine(QFrame):
    def __init__(self):
        super(QHLine, self).__init__()
        self.setFrameShape(QFrame.HLine)
        self.setFrameShadow(QFrame.Sunken)