from PyQt5.Qt import *

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import pandas as pd
import random
from GUI.calibrate import *
from pandas.core.api import DataFrame
import numpy as np


class GraficWindow(QDialog):
    def __init__(self, parent=None):
        super(GraficWindow, self).__init__(parent)
        self.figure = plt.figure(figsize=(20, 15))
        self.canvas = FigureCanvas(self.figure)
        self.toolbar = NavigationToolbar(self.canvas, self)
        self.button = QPushButton('Построить график')
        self.button.clicked.connect(self.plot)
        layout = QVBoxLayout()
        layout.addWidget(self.toolbar)
        layout.addWidget(self.canvas)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def plot(self):
        df = pd.read_excel('table_for_grafics.xlsx')
        data_table_calibrate = df.copy()
        data_1_channel = DataFrame()
        data_2_channel = DataFrame()
        data_3_channel = DataFrame()
        data_4_channel = DataFrame()
        data_5_channel = DataFrame()
        data_6_channel = DataFrame()
        data_7_channel = DataFrame()
        data_8_channel = DataFrame()
        data_9_channel = DataFrame()
        data_10_channel = DataFrame()
        data_11_channel = DataFrame()
        data_12_channel = DataFrame()
        data_13_channel = DataFrame()
        data_14_channel = DataFrame()
        data_15_channel = DataFrame()
        data_16_channel = DataFrame()
        data_17_channel = DataFrame()
        data_18_channel = DataFrame()
        data_19_channel = DataFrame()
        data_20_channel = DataFrame()
        data_21_channel = DataFrame()
        data_22_channel = DataFrame()
        data_23_channel = DataFrame()
        data_24_channel = DataFrame()
        data_25_channel = DataFrame()
        data_26_channel = DataFrame()
        data_27_channel = DataFrame()
        data_28_channel = DataFrame()
        data_29_channel = DataFrame()
        data_30_channel = DataFrame()
        data_31_channel = DataFrame()
        data_32_channel = DataFrame()

        count_step_voltage = 8
        count_channel = 32
        for i in range(0, count_step_voltage):
            data_1_channel = data_1_channel.append(
                ([data_table_calibrate['K_kalibrate'][i * count_channel]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_2_channel = data_2_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 1]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_3_channel = data_3_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 2]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_4_channel = data_4_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 3]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_5_channel = data_5_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 4]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_6_channel = data_6_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 5]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_7_channel = data_7_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 6]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_8_channel = data_8_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 7]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_9_channel = data_9_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 8]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_10_channel = data_10_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 9]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_11_channel = data_11_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 10]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_12_channel = data_12_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 11]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_13_channel = data_13_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 12]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_14_channel = data_14_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 13]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_15_channel = data_15_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 14]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_16_channel = data_16_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 15]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_17_channel = data_17_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 16]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_18_channel = data_18_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 17]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_19_channel = data_19_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 18]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_20_channel = data_20_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 19]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_21_channel = data_21_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 20]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_22_channel = data_22_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 21]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_23_channel = data_23_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 22]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_24_channel = data_24_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 23]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_25_channel = data_25_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 24]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_26_channel = data_26_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 25]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_27_channel = data_27_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 26]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_28_channel = data_28_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 27]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_29_channel = data_29_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 28]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_30_channel = data_30_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 29]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_31_channel = data_31_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 30]]), ignore_index=True)
        for i in range(0, count_step_voltage):
            data_32_channel = data_32_channel.append(
                ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 31]]), ignore_index=True)

        volt = pd.unique(data_table_calibrate['Voltage'])
        voltage = DataFrame(volt, columns=['Voltage'])

        data = pd.concat([data_1_channel, data_2_channel, data_3_channel, data_4_channel,
                          data_5_channel, data_6_channel, data_7_channel, data_8_channel,
                          data_9_channel, data_10_channel, data_11_channel, data_12_channel,
                          data_13_channel, data_14_channel, data_15_channel, data_16_channel,
                          data_17_channel, data_18_channel, data_19_channel, data_20_channel,
                          data_21_channel, data_22_channel, data_23_channel, data_24_channel,
                          data_25_channel, data_26_channel, data_27_channel, data_28_channel,
                          data_29_channel, data_30_channel, data_31_channel, data_32_channel,
                          voltage], axis=1)
        data = data.set_index('Voltage')
        writer = pd.ExcelWriter('table_for_grafics_new.xlsx')
        data.to_excel(writer, 'Sheet1')
        writer.save()
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        plt.title("График калибровочных коэффициентов")

        ax.plot(voltage, data_1_channel, '*-', label=r'$Канал 1$',)
        ax.plot(voltage, data_2_channel, '*-', label=r'$Канал 2$',)
        ax.plot(voltage, data_3_channel, '*-', label=r'$Канал 3$',)
        ax.plot(voltage, data_4_channel, '*-', label=r'$Канал 4$', )
        ax.plot(voltage, data_5_channel, '*-', label=r'$Канал 5$', )
        ax.plot(voltage, data_6_channel, '*-', label=r'$Канал 6$', )
        ax.plot(voltage, data_7_channel, '*-', label=r'$Канал 7$', )
        ax.plot(voltage, data_8_channel, '*-', label=r'$Канал 8$', )
        ax.plot(voltage, data_9_channel, 'o--', label=r'$Канал 9$',)
        ax.plot(voltage, data_10_channel, 'o--', label=r'$Канал 10$',)
        ax.plot(voltage, data_11_channel, 'o--', label=r'$Канал 11$',)
        ax.plot(voltage, data_12_channel, 'o--', label=r'$Канал 12$', )
        ax.plot(voltage, data_13_channel, 'o--', label=r'$Канал 13$', )
        ax.plot(voltage, data_14_channel, 'o--', label=r'$Канал 14$', )
        ax.plot(voltage, data_15_channel, 'o--', label=r'$Канал 15$', )
        ax.plot(voltage, data_16_channel, 'o--', label=r'$Канал 16$', )
        ax.plot(voltage, data_17_channel, 's:', label=r'$Канал 17$',)
        ax.plot(voltage, data_18_channel, 's:', label=r'$Канал 18$',)
        ax.plot(voltage, data_19_channel, 's:', label=r'$Канал 19$',)
        ax.plot(voltage, data_20_channel, 's:', label=r'$Канал 20$', )
        ax.plot(voltage, data_21_channel, 's:', label=r'$Канал 21$', )
        ax.plot(voltage, data_22_channel, 's:', label=r'$Канал 22$', )
        ax.plot(voltage, data_23_channel, 's:', label=r'$Канал 23$', )
        ax.plot(voltage, data_24_channel, 's:', label=r'$Канал 24$', )
        ax.plot(voltage, data_25_channel, 'd-.', label=r'$Канал 25$',)
        ax.plot(voltage, data_26_channel, 'd-.', label=r'$Канал 26$',)
        ax.plot(voltage, data_27_channel, 'd-.', label=r'$Канал 27$',)
        ax.plot(voltage, data_28_channel, 'd-.', label=r'$Канал 28$', )
        ax.plot(voltage, data_29_channel, 'd-.', label=r'$Канал 29$', )
        ax.plot(voltage, data_30_channel, 'd-.', label=r'$Канал 30$', )
        ax.plot(voltage, data_31_channel, 'd-.', label=r'$Канал 31$', )
        ax.plot(voltage, data_32_channel, 'd-.', label=r'$Канал 32$', )
        plt.legend(loc='best', fontsize=6)

        self.canvas.draw()
