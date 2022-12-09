import time

import globus_ethernet
import base_interface_function
import stages
from GwInstek74303S.com_voltage_regulator import VoltageRegulator

VoltageRegulator.voltage_em = 27.0
voltage_regulator = VoltageRegulator()

voltage_regulator.set_port()
voltage_regulator.power_em()
voltage_regulator.set_calibrate_voltage(2.15)

globus_ethernet.Ethernet.host = '192.168.1.0'
globus_ethernet.Ethernet.port = 1233
# #                          2    6            2      6           14     18           22       14
# channel_voltage = {'1': [1.16, 4.15], '2': [1.16, 4.15], '3': [10.37, 13.24], '4': [16.54, 10.37],
#                    '5': [23.64, 27.27],  '6': [27.77, 16.36],  '7': [5.22, 16.36]}
# #                          26   30               30    18             6     18
#                          2    6            2      6           14     18           22      14
# channel_voltage = {'1': [1.16, 4.15], '2': [1.16, 4.15], '3': [10.37, 13.24], '4': [16.54, 10.37], }
# channel_voltage = {'1': [1.7, 4.15], '2': [1.16, 4.15], '3': [10.37, 13.24], '4': [16.54, 10.37], }
compare = stages.CompareLevel()
channel_voltage = {'3': [1.27, 4.29]}



logs = compare.compare_level(0, **channel_voltage)

while True:
    logs = compare.compare_level(0, **channel_voltage)
    yr_1 = (bin(logs[-1][0][3])[2:])
    yr_2 = (bin(logs[-1][1][3])[2:])
    # # time.sleep(0.001)
    print(yr_1, yr_2)
# log_old = logs[1]
# log_new = []
# for log in log_old:
#    log_new.append(log)
# log_new.reverse()
# print(log_new)
# print(bin(log_new[0]))
# print(logs)



# # bits = []
# yr_1 = (bin(logs[-1][0][3])[2:])
# yr_2 = (bin(logs[-1][1][3])[2:])
# # # time.sleep(0.001)
# print(yr_1, yr_2)
# channel = 9
# level_off = 32.0
# up_voltage_1 = 2.0
# while True:
#
#     up_voltage_1 = round(up_voltage_1, 2)
#     channel_volt = {'9': [up_voltage_1, up_voltage_1]}  # Формирование уровней
#     logs = compare.compare_level(0, **channel_volt)  # Выполнение разового компарирования
#     # log_1 = int.from_bytes(logs[0][0], byteorder='big', signed=True)
#     print(logs, up_voltage_1)