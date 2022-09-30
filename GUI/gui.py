from PyQt5.Qt import *
from PyQt5 import QtWidgets, QtGui, QtCore
from stages import *


class StageThread(QtCore.QThread):
    thread_signal = QtCore.pyqtSignal(int)
    thread_receive_data = QtCore.pyqtSignal(list)

    def __init__(self, parent=None):
        QtCore.QThread.__init__(self, parent)

    def run(self):
        # Здесь живёт отдельный поток
        st = Stages_01()
        # Ниже список с параметрами из st - экземпляра объекта Stage_01
        interface_param = CentralWindow.interface_param
        # [QStandardItem(st.name_param_01), QStandardItem(st.name_param_02),
        # QStandardItem(st.name_param_03), QStandardItem(st.name_param_04)]

        list_param = [st.parameter_01, st.parameter_02,
                      st.parameter_03, st.parameter_04] # Все параметры

        list_flag = [] # Кол-во флагов должно быть равно кол-ву параметров

        for i in interface_param:
            if i.checkState() == 0:
                list_flag.append(0)
                continue
            list_flag.append(1)

        # Вычитка буфера перед началом работы с платой не требуется
        # Исходное soft очищает буфер модуля


        # #Ниже код для запуска только выделенных параметров!!!
        for i in range(0, (len(list_flag))):

        # self.thread_receive_data.emit(receive_data)
            if list_flag[i] == 1:
                receive_data = list_param[i]()
                self.thread_receive_data.emit(receive_data)
                #QtCore.QThread.msleep(100)
            self.thread_signal.emit(i) # Передача через сигнал значения для LoadBar
            #self.thread_receive_data.emit(receive_data)


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
        self.menu_1.addAction('&Калибровка', self.calibrate)
        self.menu_1.addAction('&Выход', self.close)
        self.menu_2 = self.menuBar().addMenu("&Вид")
        self.menu_2.addAction('&Каскад', self.window_cascade)
        self.menu_2.addAction('&Плитка', self.window_tiled)
        #self.menu.triggered[QAction].connect(self.prov_tu())

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

    def calibrate(self):
        sub = QMdiSubWindow()
        sub.setWidget(CalibrateWindow(self.mdi))
        self.mdi.addSubWindow(sub)
        sub.show()

        # MDIWindow().sub_1.setVisible(True)
        # QWidget.activateWindow(CalibrateWindow)
        # sub_1 = QMdiSubWindow()
        # sub_1.setWidget(CalibrateWindow(self.mdi))
        # self.mdi.addSubWindow(sub_1)
        # # sub_1.show()
        # sub_1.show()

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


class CentralWindow(QtWidgets.QWidget): # Использовать для других окон
    # Ниже список с параметрами из st - экземпляра объекта Stage_01
    interface_param = [QStandardItem(Stages_01().name_param_01), QStandardItem(Stages_01().name_param_02),
                       QStandardItem(Stages_01().name_param_03), QStandardItem(Stages_01().name_param_04)]

    """Central Window"""
    def __init__(self, parent=None):
        super().__init__(parent)
        #sub = QMdiSubWindow()
        self.addr_IP = QtWidgets.QLabel('IP адрес устройства')
        self.add_addr_IP = QtWidgets.QLineEdit()

        self.add_addr_IP.setFixedWidth(115)
        #self.add_addr_IP.setInputMask('DDD.999.999.999;#') # Убрать!
        self.add_addr_IP.setText('192.168.0.1')
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
        self.log = QPlainTextEdit() # Создаем текстовое поля для вывода лога
        self.scroll = QScrollArea() # Создаем скролл в который засунем текстовое поле лога?

        self.layout = QGridLayout() # Создание сетки  1 - Основная

        # Фомирование первого блока интерфейса
        self.oneblock = QtWidgets.QHBoxLayout() # Создаем горизонтальный контейнер 1
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
        self.log.createStandardContextMenu() # Стандартное меню по правой клавише
        self.log.setTextInteractionFlags(Qt.TextSelectableByMouse) # Текст можно только выделить мышью
        self.log.setReadOnly(True) # Текстовое поле доступно только для чтения
        #self.log.setPlainText("Текст заглушка для проверки окна ЛОГА аглушка для проверки\n"*90) # Загружает текст в окно
        self.log.setMinimumWidth(400)

        # Создаем виджет дерева
        self.treeView = QtWidgets.QTreeView()
        self.treeView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.model = QStandardItemModel()
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
        self.progress_bar.setRange(0, 4)  # Задал 3 так как 4 параметра пока что, является слотом

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
        self.stage_thread = StageThread() # Содаем экземпляр класса StageThread
        #self.stage_thread.started.connect(self.on_started)
        self.stage_thread.finished.connect(self.on_finished)
        self.stage_thread.thread_signal.connect(self.on_change, QtCore.Qt.QueuedConnection)
        self.stage_thread.thread_receive_data.connect(self.log_update, QtCore.Qt.QueuedConnection)
        #sub.setWidget(self.setLayout(self.layout))
        #sub.show()

    def log_clear(self):
        self.log.clear()

    def on_connect(self):
        self.button_OK.setEnabled(False)  # Заблокировать кнопку
        addr_IP = self.add_addr_IP.text() # Получить введенное значение в поле
        port_IP = self.add_port_IP.text() # Получить введенное значение в поле

        # Установка addr и port
        Ethernet.port = int(port_IP)
        Ethernet.host = str(addr_IP)

        self.header_stage = QStandardItem(Stages_01().name_stage)

        self.model.appendRow([self.header_stage])  # Заголовок вложенной строки

        # # Ниже список с параметрами из st - экземпляра объекта Stage_01
        # self.iterface_param = [QStandardItem(Stages_01().name_param_01), QStandardItem(Stages_01().name_param_02),
        #                        QStandardItem(Stages_01().name_param_03), QStandardItem(Stages_01().name_param_04)]

        for i in self.interface_param:
            i.setCheckable(True)  #  Добавление флажка
            i.setCheckState(2)   # Задание по умолчанию флаг активен

            self.header_stage.appendRow(i)  # Вывод строк для дерева списка

        self.button_addition.setEnabled(True)  # Раблокировать кнопку
        self.button_calibrate.setEnabled(True)  # Раблокировать кнопку
        self.button_calibrate.clicked.connect(self.calibrate)
        self.model.setHorizontalHeaderLabels(['Наименование проверок', 'Результат'])
        self.treeView.setModel(self.model)  # Вывод дерева списка
        self.treeView.setColumnWidth(0, 350)  # Задать ширину 1 столбца
        self.treeView.expandAll()  # Отобразить все дочерние элементы раскрыть дерево

        # ############################################
        # self.stage_thread.start()  # Запускаем поток
        # ############################################


    def on_started(self): # Запускается в начале потока
        pass

    def on_finished(self): # Запускается после окончания выполнения потока просто для наглядности
        #self.button_OK.setEnabled(True) # Разблокировать кнопку
        self.stage_thread.yieldCurrentThread() # Принудительное завершение потока

        #pass

    def on_change(self, i): # Принимаем число из потока в Progressbar
        #self.log.setTextCursor(i[0])

        #self.stage_thread.thread_receive_data.connect(self.updatelog)
        self.progress_bar.setValue(i + 1)

    def log_update(self, text):

        print(text[0][1][0:2])
        text_read= f'READ-'\
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
        #str_log =


        #print(self.log.__slots__)


    def run_thread(self):
        self.stage_thread.start()  # Запускаем поток

    def reset_all(self):
        for i in self.interface_param:
            i.setCheckState(0)   # Задание по умолчанию флаг неактивен
            self.header_stage.appendRow(i)  # Вывод строк для дерева списка

    def set_all(self):
        for i in self.interface_param:
            i.setCheckState(2)   # Задание по умолчанию флаг активен
            self.header_stage.appendRow(i)  # Вывод строк для дерева списка

    def calibrate(self):
        #sub = QMdiSubWindow()

        sub = QMainWindow()
        sub.setCentralWidget(CalibrateWindow())
        sub.addDockWidget()
        sub.widge
        sub.setFixedWidth(600)
        sub.setWidget(CalibrateWindow())
        #self.mdi.addSubWindow(sub)
        sub.show()
        #CalibrateWindow()


class CalibrateWindow(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QGridLayout()  # Создание сетки - Основная

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
        self.button_write_voltage.setFixedWidth(150)

        # Фомирование первого блока интерфейса

        self.oneblock.addWidget(self.nmb_label, Qt.AlignLeft)
        self.oneblock.addWidget(self.nmb_channel, Qt.AlignLeft)
        self.oneblock.addWidget(self.step_label, Qt.AlignLeft)
        self.oneblock.addWidget(self.step, Qt.AlignJustify)
        self.oneblock.addWidget(self.vector_label, Qt.AlignJustify)
        self.oneblock.addWidget(self.vector_calibrate, Qt.AlignJustify)
        self.oneblock.addWidget(self.button_write_voltage, Qt.AlignJustify)

        #self.button_OK.clicked.connect(self.on_connect)

        self.oneblock.addStretch(100)
        self.layout.addLayout(self.oneblock, 0, 0, 0, 0)


        # Вывод содержимого сетки на экран
        self.setLayout(self.layout)






