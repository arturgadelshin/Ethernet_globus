from globus_ethernet import Ethernet
from base_interface_function import smk
from GwInstek74303S.com_voltage_regulator import VoltageRegulator

VoltageRegulator.voltage_em = 27.0
voltage_regulator = VoltageRegulator()

voltage_regulator.set_port()
voltage_regulator.power_em()
voltage_regulator.set_calibrate_voltage(2.15)

Ethernet.host = '192.168.1.0'
Ethernet.port = 1233

write = smk('01')
data = Ethernet().swap(write)

print(data[1])
