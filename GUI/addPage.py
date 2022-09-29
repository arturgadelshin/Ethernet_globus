# -*- coding: utf-8 -*-

import sys

from PyQt5.QtWidgets import QApplication , QMainWindow

from gui1 import *


class AddDlg(object):

    def setupUi(self, MainWindow):
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        self.mainwindows = MainWindow
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setMouseTracking(False)
        self.centralwidget.setObjectName("centralwidget")
        self.textBrowser = QtWidgets.QTextBrowser(self.centralwidget)
        self.textBrowser.setGeometry(QtCore.QRect(30, 40, 751, 221))
        self.textBrowser.setObjectName("textBrowser")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(30, 20, 191, 17))
        self.label.setObjectName("label")
        self.label_2 = QtWidgets.QLabel(self.centralwidget)
        self.label_2.setGeometry(QtCore.QRect(40, 306, 171, 31))
        self.label_2.setObjectName("label_2")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(40, 350, 171, 27))

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.label.setText(_translate("MainWindow", "Current Configuration"))
        self.pushButton.setText(_translate("MainWindow", "Add Config"))
        self.pushButton_2.setText(_translate("MainWindow", "Modify Config"))
        self.label_3.setText(_translate("MainWindow", "Add new configuration"))
        self.label_4.setText(_translate("MainWindow", "Modify Configuration"))
        self.label_5.setText(_translate("MainWindow", "Delete Configuration"))

        self.pushButton.clicked.connect(self.addClicked)


if __name__ == '__main__':

    app = QApplication(sys.argv)
    mainWindow = QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(mainWindow)
    mainWindow.show()
    sys.exit(app.exec_())

