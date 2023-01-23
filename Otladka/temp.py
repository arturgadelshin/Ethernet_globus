import time

from globus_ethernet import Ethernet
from special_interface_function import request_temperature
from base_interface_function import data_request
from GwInstek74303S.com_voltage_regulator import VoltageRegulator
#
# VoltageRegulator.voltage_em = 27.0
# voltage_regulator = VoltageRegulator()
#
# voltage_regulator.set_port()
# voltage_regulator.power_em()
# voltage_regulator.set_calibrate_voltage(2.15)

Ethernet.host = '192.168.1.0'
Ethernet.port = 1233


write = request_temperature()
Ethernet().swap(write)
time.sleep(3.0)
Ethernet().swap(write)
write = data_request(0)
data = Ethernet().swap(write)
rez_temp = data[1][-4:]
rez_temp = rez_temp[0:3]
if rez_temp[0] == 1:
    rez_temp = rez_temp[0:2]
    int_temp = -(int.from_bytes(rez_temp[1:3], byteorder='little') + 1) * 0.0625
    print(f'Температура: {int_temp}')
else:
    int_temp = int.from_bytes(rez_temp[1:3], byteorder='little') * 0.0625
    print(f'Температура: {int_temp}')



