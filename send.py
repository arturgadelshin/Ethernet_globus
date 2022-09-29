import sys
import string
import struct
import re
from base_interface_function import reset_em


# class Counter:
#     def __iter__(self):
#         self.i = 0
#         return self
#
#     def __next__(self):
#         if self.i <= 65534:
#             # x = self.a
#             self.i += 1
#             uid = struct.pack("<H", self.i)
#             return uid
#
#         else:
#             self.i = 0
#
#
# myclass = Counter()
# uid = iter(myclass)

#for x in uid:
   # if x == None:
   #     continue
   # print(x)


# Узнать как вычислять указатель на следующую команду
# Используется для вычисления указателя на следующую
# команду в UDP-пакете


def len_command(msg):
    len_command = [0, 0]
    len_c = int(len(msg) + 2)
    a = struct.pack('>h', len_c)
    size_d = bytearray(a)
    len_command[0] = int(size_d[1])
    len_command[1] = int(size_d[0])
    return len_command



def len_command_old(msg):
    a = [0,0]
    len_command = int(len(msg) + 2)
    #b = bin(len_command)
    b = ''
    print(len(msg))

    while (len_command) > 0:
        b = str(len_command % 2) + b
        len_command = len_command // 2


    if int(b) < 100000000:
        print('меньше')
        a[0] = int(b)
        a[1] = 0
    elif int(b) >= 100000000:
        i = 0
        while i < len(b):
            if i + 10 < len(b):
                a.append(str[i:i + 10])
            else:
                a.append(str[i:len(b)])
            i += 10
        #a[0] = a_byte[0]
        #a[1] = a_byte[1]

        #print(a_[1])
        #a[0] = a_byte[0]
        #a[1] = a_byte[1]

    print(a[0])
    print(a[1])

    #len_command[0] = (byte) (width & 0XFF)

    return len(msg) + len_command



class CodeCommand:

    def __init__(self):
        pass


class Reserved:

    def __init__(self):
        pass


# Дополнительные данные есть у Грушина
class AddData:

    def __init__(self):
        pass

