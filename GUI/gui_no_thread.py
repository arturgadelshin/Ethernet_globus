from PyQt5.Qt import *
from PyQt5 import QtWidgets, QtGui, QtCore
from stages import *


# class StageThread(QtCore.QThread):
#     thread_signal = QtCore.pyqtSignal(str)
#
#     def __init__(self, parent = None):
#         QtCore.QThread.__init__(self, parent)
#
#     def run(self):
#         # Здесь живёт отдельный поток
#         pass





class CentralWindow(QtWidgets.QWidget): # Использовать для других окон

    """Central Window"""
    def __init__(self, parent=None):
        super().__init__(parent)

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
        self.kostil = QtWidgets.QLineEdit()
        self.kostil.setEnabled(False)
        self.treeView = QtWidgets.QTreeView() # Создаем виджет дерева
        self.log = QPlainTextEdit() # Создаем текстовое поля для вывода лога
        self.scroll = QScrollArea() # Создаем скролл в который засунем текстовое поле лога?

        self.layout = QGridLayout() # Создание сетки  1 - Основная

        # Фомирование первого блока интерфейса
        self.oneblock = QtWidgets.QHBoxLayout() # Создаем горизонтальный контейнер 1
        self.oneblock.addWidget(self.addr_IP, )
        self.oneblock.addWidget(self.add_addr_IP, )
        self.oneblock.addWidget(self.port_IP, )
        self.oneblock.addWidget(self.add_port_IP, )
        self.oneblock.addWidget(self.button_OK, )
        self.button_OK.clicked.connect(self.on_connect)
        self.oneblock.addWidget(self.kostil)
        #self.oneblock.addSpacing(0)# Пружинка

        # Конец формирования первого блока интерфейса


        self.layout.addLayout(self.oneblock, 0, 0,1,4)
        self.layout.addLayout(self.oneblock,0,1,2,4)

        #self.layout.addWidget(self.button_OK, 1, 0)

        # Фомирование второго блока интерфейса
        self.layout_2 = QGridLayout()  # Создание сетки 2 блока
        self.twoblock = QtWidgets.QHBoxLayout()  # Создаем горизонтальный контейнер 2

        self.log.documentTitle() # Задаем заголовок документа
        # Настройка log
        self.log.createStandardContextMenu() # Стандартное меню по правой клавише
        self.log.setTextInteractionFlags(Qt.TextSelectableByMouse) # Текст можно только выделить мышью
        self.log.setReadOnly(True) # Текстовое поле доступно только для чтения
        self.log.setPlainText("Текст заглушка для проверки окна ЛОГА аглушка для проверки\n"*90) # Загружает текст в окно
        self.log.setMinimumWidth(400)
        self.comboBox = QtWidgets.QComboBox()




        # Создаем виджет дерева
        self.treeView = QtWidgets.QTreeView()
        self.treeView.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.model = QStandardItemModel()
        #self.treeView.setModel(self.model)
        self.treeView.setUniformRowHeights(True)




        # Добавляем виджеты в сетку
        self.layout.addWidget(self.treeView,1, 0, )
        #self.layout.addWidget(self.treeView, 1, 0, Qt.AlignHCenter)
        self.layout.addWidget(self.log, 1, 2, Qt.AlignRight )

        self.layout.setContentsMargins(10, 10, 10, 10)  # Формирование отступов

        self.button_RUN = QtWidgets.QPushButton("Начать проверку")
        self.button_RUN.setFixedWidth(100)
        self.button_RUN.clicked.connect(self.run_test)
        # Ниже создан прогресс бар
        self.progress_bar = QtWidgets.QProgressBar()
        #self.progress_bar.setMinimum(0)
        #self.progress_bar.setMaximum(3)
        self.progress_bar.setRange(0,4) # Задал 3 так как 4 параметра пока что, является слотом


        self.button_CLEAR = QtWidgets.QPushButton("Очистить лог")
        self.button_CLEAR.setFixedWidth(100)


        self.layout.addWidget(self.button_RUN, 2, 0, Qt.AlignLeft)
        self.layout.addWidget(self.progress_bar, 2, 0, Qt.AlignJustify)
        self.layout.addWidget(self.button_CLEAR, 2, 2, Qt.AlignLeft)

        # Вывод содержимого сетки на экран
        self.setLayout(self.layout)


        # label_IP.indent()
        # label_IP.setAlignment(Qt.AlignBottom | Qt.AlignRight)
        # phoneLabel = QLabel("&Phonehkjhkhkjhkjh:", self) # Назначаем подпись Вариант 2
        # phoneLabel.setBuddy(label_IP)


    def on_connect(self):
        self.button_OK.setEnabled(False)  # Заблокировать кнопку
        addr_IP = self.add_addr_IP.text() # Получить введенное значение в поле
        port_IP = self.add_port_IP.text() # Получить введенное значение в поле

        # Установка addr и port
        Ethernet.port = int(port_IP)
        Ethernet.host = str(addr_IP)

        #self.eth_new = Ethernet()
        self.st = Stages_01()

        header_stage = QStandardItem(self.st.name_stage)


        self.model.appendRow([header_stage]) # Заголовок вложенной строки

        # Ниже список с параметрами из st - экземпляра объекта Stage_01
        self.iterface_param = [QStandardItem(self.st.name_param_01), QStandardItem(self.st.name_param_02),
                               QStandardItem(self.st.name_param_03), QStandardItem(self.st.name_param_04)]

        for i in self.iterface_param:
            i.setCheckable(True) #  Добавление флажка
            i.setCheckState(2)   # Задание по умолчанию флаг активен
            header_stage.appendRow(i) # Вывод строк для дерева списка

        self.model.setHorizontalHeaderLabels(['Наименование проверок', 'Результат'])
        self.treeView.setModel(self.model) # Вывод дерева списка
        self.treeView.setColumnWidth(0, 350) # Задать ширину 1 столбца
        self.treeView.expandAll()  # Отобразить все дочерние элементы раскрыть дерево


    def run_test(self):

        list_param = [self.st.parameter_01, self.st.parameter_02,
                      self.st.parameter_03, self.st.parameter_04] # Все параметры
        # Метод который выполняется при нажатии кнопки "Начать проверку"
        list_flag = [] # Кол-во флагов должно быть равно кол-ву параметров
        for i in self.iterface_param:
            if i.checkState() == 0:
                list_flag.append(0)
                continue
            list_flag.append(1)

        # Вычитка буфера перед началом работы с платой не требуется
        # Исходное soft очищает буфер модуля

        #Ниже код для запуска только выделенных параметров!!!
        for i in range(0, (len(list_flag))):

            if list_flag[i] == 1:
                list_param[i]()
            #self.progress_bar.setValue(i) #Увеличить значение в прогресс баре
            self.progress_bar.setValue(i+1)















class MainWindow(QMainWindow): # Использовать для основного окна
    """Main Window."""
    def __init__(self, parent=None):
        """Initializer."""
        super().__init__(parent)
        self.setCentralWidget(CentralWindow()) # Вызов в центральный виджет своего виджета
        self._createMenu()
        #self._createToolBar()
        self.statusBar = QStatusBar()
        self.setStatusBar(self.statusBar)

    def _createMenu(self):
        self.menu = self.menuBar().addMenu("&Menu")
        self.menu.addAction('&Exit', self.close)

    def _createToolBar(self):
        tools = QToolBar()
        self.addToolBar(tools)
        tools.addAction('Exit', self.close)

    def _createStatusBar(self, text):
        print(text)
        self.statusBar.showMessage(text, 1)


    def _clearMessage(self):
        print('ggg')
        #self.status.clearMessage()
        #self._createStatusBar.clearMessage()


