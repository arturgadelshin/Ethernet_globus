import glob
import time
import serial
import os
import sys
import io

def serial_ports():
    """ Lists serial port names

        :raises EnvironmentError:
            On unsupported or unknown platforms
        :returns:
            A list of the serial ports available on the system
    """
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        # this excludes your current terminal "/dev/tty"
        ports = glob.glob('/dev/tty[A-Za-z]*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/tty.*')
    else:
        raise EnvironmentError('Unsupported platform')

    result = []
    for port in ports:
        try:
            s = serial.Serial(port)
            s.close()
            result.append(port)
        except (OSError, serial.SerialException):
            pass
    return result


class VoltageRegulator:
    speeds = ['1200','2400', '4800', '9600', '19200', '38400', '57600', '115200']
    comport = 'COM3'
    speed = '9600'
    channel_em = 1
    channel_calibrate = 2
    voltage_em = 0

    def set_port(self):
        self.port = serial.Serial(self.comport, self.speed)
        time.sleep(2)

    # def set_voltage(self, voltage):
    #     self.port.write(bytes(str(voltage), 'utf-8'))
    #     time.sleep(1.0)
    #     self.port.write(bytes(str(voltage), 'utf-8'))
    #     time.sleep(1.0)  # Необходимая задержка на время установления напряжения на выходе регулятора

    def power(self, logic): # Включение/выключение источника
        if logic == 1:
            on = 'OUT1'+'\n'
            self.port.write(bytes(on, 'utf-8'))
        if logic == 0:
            off = 'OUT0'+'\n'
            self.port.write(bytes(off, 'utf-8'))
        time.sleep(1.0)

    def i_set(self, channel, i):  # Задание тока поканально
        return 'ISET'+str(channel)+':'+str(i)+'\n'

    def v_set(self, channel, u):  # Задание напряжение поканально
        return 'VSET'+str(channel)+':'+str(u)+'\n'

    def track(self, set): # Задание режима работы
        # По дефолту 0 - независимые каналы
        return 'TRACK' + str(set)+'\n'

    def power_em(self):
        i1 = self.i_set(self.channel_em, 0.7)
        self.port.write(bytes(i1, 'utf-8'))
        time.sleep(0.02)
        #print(self.port.read(20))
        v1 = self.v_set(self.channel_em, self.voltage_em)
        self.port.write(bytes(v1, 'utf-8'))
        time.sleep(0.02)
        i2 = self.i_set(self.channel_calibrate, 0.1)
        self.port.write(bytes(i2, 'utf-8'))
        time.sleep(0.02)
        v2 = self.v_set(self.channel_calibrate, 0.0)
        self.port.write(bytes(v2, 'utf-8'))
        time.sleep(0.02)
        self.power(1)

    def set_calibrate_voltage(self, voltage):
        v1 = self.v_set(self.channel_calibrate, voltage)
        self.port.write(bytes(v1, 'utf-8'))
        time.sleep(0.05)



