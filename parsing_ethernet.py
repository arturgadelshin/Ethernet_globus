 # Здесь будет происходить парсинг ответной посылки от модуля
# НИЖЕ ОТВЕТ НА КОМАНДУ ИСХОДНОЕ
"""
  0x00, 0x00, 0x89, 0x00, 0xf0, 0x03, 0x00, 0x00,
  0x00, 0x00, 0x00, 0x00, 0x0a, 0x00, 0x0a, 0x00,
  0xd6, 0xbe, 0xc4, 0x04, 0x00, 0x04, 0x0a, 0x00,
  0x0a, 0x00, 0xda, 0xbe, 0xc4, 0x04, 0x00, 0x03
  
  """
# 00008900f0030000000000000a000a00d6bec40400040a000a00dabec4040003

recieve = b'\x00\x01\x89\x00\x00\x00\x00\x01\x00\x00\x00\x00\n\x00\n\x00y\x8eI\x05\x01\x01'

recieve_clean = b'\x00\x00\x89\x00\xf0\x03\x00\x00\x00\x00\x00\x00\x0a\x00\x0a\x00\xd6\xbe\xc4\x04\x00\x04\x0a\x00\x0a\x00\xda\xbe\xc4\x04\x00\x03'


# Функция которая может конвертировать системы исчисления
def convert_base(num, to_base=10, from_base=10):
    # first convert to decimal number
    if isinstance(num, str):
        n = int(num, from_base)
    else:
        n = int(num)
    # now convert decimal to 'to_base' base
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    if n < to_base:
        return alphabet[n]
    else:
        return convert_base(n // to_base, to_base) + alphabet[n % to_base]


class Parsing:

    def info_packet(self, packet):
        data = bytearray(packet)
        info =[]
        print("-----------------Информация о пакете-----------------------")
        print("UID: ", (data[0:2]))
        print("Reg State: ", data[2:4])
        print("Head: ", data[4:8])
        print("Tail: ", data[8:12])
        print("Len command: ", data[12:14])
        print("Mark type: ", data[14])
        print("Time: ", data[15:20])
        print("Code command: ", data[20])
        print("State command: ", data[21])
        print("Data?", data[22:])
        print("-----------------Конец информации пакете-----------------------")
        info.append(data[22:])
        return data

    def reg_state_packet(self, *args):
        # 1 - аргумент сам пакет, 2 - младший байт маски 3 - старший байт маски
        mask_ll = 'FF'
        mask_bb = 'FF'
        # 0 READY
        # 1 BUSY
        # 2 EXT_CLK
        # 3 SERVICE
        # 4 RW_DATA
        # 5 FAULT_HANDLED
        # 6 START_DST
        # 7 START_SRC
        # 8..15 RESERVED
        msg = []
        res = ["Признак ожидания модулем события для выдачи сигнала на триггерную линию Tr3+ <<Запуск>> ",
                "Признак ожидания модулем сигнала на триггерной линии Tr3+ <<Запуск>> для выполнения заданной команды",
               "Признак отработки события по триггерной линии Tr10 Авария",
               "Признак перезаписи непрочитанных данных в кольцевом буфере",
               "Признак нештатной ситуации",
               "Признак работы таймера на внешней частоте",
               "Признак занятости модуля выполнением команды",
               "Признак готовности к выполнению команды",
                ]

        b = [0, 0]
        try:
            mask_l = args[1]
            mask_b = args[2]
        except IndexError:
            mask_l = mask_ll
            mask_b = mask_bb

        mask_hex_l = int(mask_l, 16)
        mask_hex_f = int(mask_b, 16)
        packet_byte = bytearray(args[0])
        header_packet = packet_byte[0:12]

        b0 = int((header_packet[2]))
        b1 = int(header_packet[3])

        b[0] = b0 & mask_hex_l
        b[1] = b1 & mask_hex_f
        bits = bin(b[0])[2:]

        print("-----------------Регистр состояния-----------------------")
        for i in range(len(bin(b[0])[2:])):
            if bits[i] == '1':
                msg.append(res[i])
                print(res[i])
        print("-----------------Конец Регистра состояния----------------")

        return bits, msg

    def buffer_packet(self, packet):
        """
        При выдаче команды чтение данных с произвольного адреса данные из ОЗУ Модуля
        берутся и докладываются в буфер Ethernet, соответственно голова увеличивается.
        При выдаче команды запрос данных, данные вычитываются из буфера Ethernet,
        соответственно увеличивается хвост. Как только хвост равен голове, то вычитали
        все данные.
        :param packet:
        :return:
        """
        # принимаем пакет
        packet_byte = bytearray(packet)
        #packet_byte = packet

        # берем из пакета голову
        head_packet = packet_byte[4:8]
        # переворачиваем голову
        head_packet.reverse()
        res_head = convert_base(head_packet.hex(), from_base=16, to_base=10)

        # берем из пакета хвост
        tail_packed = packet_byte[8:12]
        # переворачиваем хвост
        tail_packed.reverse()
        res_tail = convert_base(tail_packed.hex(), from_base=16, to_base=10)

        return head_packet, tail_packed

    def identifier_type(self, packet):
        res = ["Значение регистра СМК", # 0x08
               "Значение после записи 32х бит по маске", # 0x09
               "Подтверждение команды приёма", # 0x0A
               "Результат чтения данных с произвольного адреса, значение после записи \n 32х бит по маске ", # 0x0B
               "Изменение состояния триггерных линий", # 0x0C
               "Результат измерения", # 0x10
               "Результат калибровки", # 0x11
                ]
        type_ = [
            0x08,
            0x09,
            0x0A,
            0x0B,
            0x0C,
            0x10,
            0x11,
        ]
        msg = []
        identifier_type = bytearray(packet)[12]

        print("-----------------Идентификатор типа----------------------")
        for i in range(len(type_)):
            if type_[i] == identifier_type:
                msg.append(res[i])
                print(res[i])
        print("-----------------Конец идентификатора типа---------------")
        return msg

    def time(self, packet):
        b = [0, 0, 0, 0, 0]
        # принимаем пакет
        time = bytearray(packet)[13:18]
        # формируем правильный массив байт
        b[0] = int(time[0])
        b[1] = int(time[4])
        b[2] = int(time[3])
        b[3] = int(time[2])
        b[4] = int(time[1])
        res_head = convert_base(bytes(b).hex(), from_base=16, to_base=10)
        micros = int(res_head)
        print("-----------------Время на таймере------------------------")
        print(micros)
        print("-----------------Конец времени на таймере----------------")
        return micros

    def reply_confirm_command(self, packet):
        msg = []
        res = [
            "Команда выполнена",
            "Начато выполнение команды",
            "Останов по ошибке",
            "Неизвестная команда",
            "Невыполняемая команда",
        ]
        confirm_command = bytearray(packet)[20:22]
        command = int(confirm_command[0])
        state_command = int(confirm_command[1])

        print("-----------------Ответ подтверждения команды-------------")
        for i in range(1, len(res)):
            if i == state_command:
                msg.append(res[i-1])
                print(res[i-1])
        print("-----------------Конец ответа подтверждения команды------")
        return command, msg

    def info_parsing_packet(self, packet):
        self.reg_state_packet(packet)
        self.identifier_type(packet)
        self.time(packet)
        self.reply_confirm_command(packet)

    def return_data_packet(self, packet):
        byte =[0]*16
        res_x0C = [
               "Состояние Tr2+ -> Счет таймера: ",
               "Состояние Tr3+ -> Выдан ЗАПУСК: ",
               "Состояние Tr3+ -> Получен ЗАПУСК: ",
               "Состояние Tr10 -> Выдана АВАРИЯ: ",
               "Состояние Tr10 -> Получена АВАРИЯ: ",
               ]
        msg = []
        identifier_type = bytearray(packet)[12]
        if int(identifier_type) == 12:# 0x0C
            data = bytearray(packet)[22:24]
            # Получение битов
            bits = bin(data[0])[2:]
            for i in range(len(bits)):
                byte[i] = bits[i]
            print("-----------------Состояние триггерных линий--------------")
            for i in range(len(res_x0C)):
                msg.append(res_x0C[i]+str(byte[i]))
                print(msg[i])
            print("-----------------Конец состояния триггерных линий--------")
            return msg
        else:
            data = bytearray(packet)[22:]
            msg.append(data)
            print(msg)
            return msg


class WindowParsing(Parsing):

    def info_packet(self, packet):
        data = bytearray(packet)
        # info = {
        #     'uid': data[0:2],
        #     'regstate': data[2:4],
        #     'head': data[4:8],
        #     'tail': data[8:12],
        #     'lencommand': data[12:14],
        #     'marktype': data[14],
        #     'time': data[15:20],
        #     'codecommand': data[20],
        #     'statecommand': data[21],
        #     'data': data[22:],
        # }
        return data


#rec.identifier_type(recieve)
#rec.reg_state_packet(recieve)
#print(rec.time(recieve))
#rec.reply_confirm_command(recieve)
#rez = rec.buffer_packet(recieve)
#print(rez)
#rec.info_packet(recieve)
#rec.return_data_packet(recieve)