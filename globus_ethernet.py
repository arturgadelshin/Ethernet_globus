import struct

import logging
import socket
import time
import timeit

from base_interface_function import*
from send import len_command


class UID:
    """Класс обеспечивает бесконечное последовательное перечисление до 65535."""
    def __init__(self):
        # Здесь хранится промежуточное значение
        self.number = 0

    def __next__(self):
        # Здесь мы обновляем значение и возвращаем результат
        if self.number == 65535:
            self.number = -1
        while self.number < 65535:
            self.number = self.number + 1
            self.bytes = struct.pack('<H', self.number)
            # bytes[0] - старший байт bytes[1] - младший байт
            #print(self.bytes[0])
            #print(self.bytes[1])
            return self.bytes

    def __iter__(self):
        """Этот метод позволяет при передаче объекта функции iter возвращать самого себя, тем самым в точности реализуя протокол итератора."""
        return self

    def old(self):
        return self.bytes


class Ethernet:
    """ Класс для работы с ethernet, настройка абоненета, прием-передача """
    uid_2_byte = UID() # Создание объекта UID
    host = '0'
    port = 0

    def __init__(self):
        pass

    def swap(self, command):
        em = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,)  # Установка типа сети UPD
        em.connect((self.host, self.port))
        #socket.setdefaulttimeout(5) # Настройка таймаута
        uid = next(self.uid_2_byte)
        len_com = len_command(command)
        com = command
        list_uid = bytes([(uid[0]), uid[1]])
        write = list_uid+len_com+com
        #print('*'*57)
        em.sendall(write)
        #time.sleep(0.15)
        #data = self.client.recvfrom(1024,2) # Волшебная строчка!
        read = em.recvfrom(1024)
        # Попробовать функцию recv
        em.close()
        return [write, read[0]]


    def delay_swap(self, command):
        em = socket.socket(socket.AF_INET, socket.SOCK_DGRAM,)  # Установка типа сети UPD
        em.connect((self.host, self.port))
        # socket.setdefaulttimeout(30) # Настройка таймаута
        uid = next(self.uid_2_byte)
        len_com = len_command(command)
        com = command
        list_uid = bytes([(uid[0]), uid[1]])
        write = list_uid+len_com+com
        #print('*'*57)
        em.sendall(write)
        time.sleep(3)
        #data = self.client.recvfrom(1024,2) # Волшебная строчка!
        read = em.recvfrom(1024)
        em.close()
        return [write, read[0]]
