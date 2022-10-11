import glob
import time
import serial
import os
import sys


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
    port = ''
    speed = ''

    def set_port(self):
        self.port = serial.Serial(self.port, self.speed)
        time.sleep(2)

    def set_voltage(self, voltage):
        self.port.write(bytes(str(voltage), 'utf-8'))
        time.sleep(1.0)
        self.port.write(bytes(str(voltage), 'utf-8'))
        time.sleep(1.0)  # Необходимая задержка на время установления напряжения на выходе регулятора

