from base_interface_function import*
from logging import *
from globus_ethernet import *
from parsing_ethernet import *
import time
from GUI.calibrate import *


class Stages_01():
    "Итерфейсный блок"
    pars = Parsing() # Создание объекта Парсера, для распарсивания принятых пакетов
    recieve_data = WindowParsing()
    #eth = Ethernet()
    #eth = Ethernet('192.168.0.1', 1233)


    def __init__(self):
        self.stage = 'Наименование проверки'
        self.name_stage = 'Проверка интерфесных фукнций'
        self.name_param_01 = 'Исходное Soft'
        self.name_param_02 = 'Исходное Hard'
        self.name_param_03 = 'Чтение тестовой информации без сброса'
        self.name_param_04 = 'Чтение тестовой информации со сбросом'
        self.state = [1, 1, 1, 1]  # Кол-во состояний равно кол-ву параметров
        add_log_file(self.stage + ' - ' + self.name_stage)

    def parameter_01(self):
        write = reset_em(0)
        add_log_file(self.name_param_01)
        data = Ethernet().swap(write)
        self.pars.info_packet(data[1])
        add_log_file(data[1])
        must_be = ''
        valid = True
        return [data, must_be, valid]

    def parameter_02(self):
        write = reset_em(1)
        add_log_file(self.name_param_02)
        data = Ethernet().delay_swap(write)
        self.pars.info_packet(data[1])
        add_log_file(data[1])
        must_be = ''
        valid = True
        return [data, must_be, valid]

    def parameter_03(self):
        write = read_testinfo_and_rgsmk(0)
        add_log_file(self.name_param_03)
        data = Ethernet().swap(write)
        self.pars.info_packet(data[1])
        add_log_file(data[1])
        must_be = ''
        valid = True
        return [data, must_be, valid]

    def parameter_04(self):
        write = read_testinfo_and_rgsmk(1) # Было так
        add_log_file(self.name_param_04)
        data = Ethernet().swap(write)
        self.pars.info_packet(data[1])
        add_log_file(data[1])
        must_be = ''
        valid = True
        return [data, must_be, valid]

    def all_parameters(self):
        self.parameter_01()
        self.parameter_02()
        self.parameter_03()
        self.parameter_04()


class Stages_02:
    "Блок с IP адресом"
    pars = Parsing()  # Создание объекта Парсера, для распарсивания принятых пакетов
    recieve_data = WindowParsing()

    def __init__(self):
        self.name_stage = 'СМК'
        self.name_param_01 = 'Проведение самоконтроля модуля'
        add_log_file(self.name_stage)

    def parameter_01(self):
        must_be = ''
        write = smk('01')
        add_log_file(self.name_param_01)
        data = Ethernet().swap(write)
        self.pars.reg_state_packet(data[1])
        add_log_file(data[1])
        #valid = True
        recieve_data = data[1][21]    # Получаем статус команды
        if hex(recieve_data) == hex(0x01):  #[0x02] - из протокола проверки МКС
            valid = True
        else:
            valid = False
        return [data, must_be, valid]

    def parameter_02(self, repeat):
        pass


class Calibrate:
    """ Класс который описывает калибровку каждого канала """
    pars = Parsing()  # Создание объекта Парсера, для распарсивания принятых пакетов
    recieve_data = WindowParsing()

    def __init__(self):
        # Может сюда стоит добавить команду сброса soft ?
        ...

    def write_voltage_for_calibrate(self, step, vector, channel):
        write = calibrate(step, vector, channel)  # code command 0x80
        data = Ethernet().swap(write)
        must_be_bytes = {
            2: [1],
            12: [10],   # 0x0A
            14: [10],   # 0x0A
            20: [128],  # 0x80
            21: [1],
        }
        # must_be = 5
        # for i, byte in enumerate(data[1]):
        #     try:
        #         if [byte] == must_be_bytes[i]:
        #             must_be -= 1
        #     except KeyError:
        #         continue
        # if must_be == 0:
        #     print(f"Команда {bytes(must_be_bytes[20])} выполнена")
        # else:
        #     print(f"Команда {bytes(must_be_bytes[20])} невыполнена")


        # Даю задержку на время выполнения калибровки
        #time.sleep(0.1)

        # Чтение данных командой запрос данных
        write = data_request(0)
        data = Ethernet().swap(write)
        must_be_bytes = {
            2: [1],
            12: [10],  # 0x0A
            14: [10],  # 0x0A
            20: [4],  # 0x80
            21: [1],
        }
        # must_be = 5
        # for i, byte in enumerate(data[1]):
        #     try:
        #         if [byte] == must_be_bytes[i]:
        #             must_be -= 1
        #     except KeyError:
        #         continue
        # if must_be == 0:
        #     print(f"Команда {bytes(must_be_bytes[20])} выполнена")
        # else:
        #     print(f"Команда {bytes(must_be_bytes[20])} невыполнена")

        frame = data[1][22:30]  # frame так сказал Юрий Иваныч Атаманчук
        channel_read = data[1][30]
        step_read = data[1][31]
        combined_byte = data[1][32]
        reserved = data[1][33]
        code_dac_1 = data[1][34:36]
        code_dac_2 = data[1][36:38]
        if step == step_read and channel == channel_read:
            print(f"Команда {bytes(must_be_bytes[20])} отработана верно")
        else:
            print(f"Команда {bytes(must_be_bytes[20])} отработана неверно")

        # возможно придется преобразовать принятый байт в bin()
        combined_byte = bin(combined_byte)
        for i, byte in enumerate(combined_byte):
            # if i == 2:
            #     if int(combined_byte[i]) == 1:
            #         print("Восходящая калиброка")
            #     if int(combined_byte[i]) == 0:
            #         print("Нисходящая калиброка")
            if i == 8:
                if int(combined_byte[i]) == 1:
                    print("На компараторе 1 достигнуло значение")
                if int(combined_byte[i]) == 0:
                    print("На компараторе 1 недостигнуло значение")
            if i == 9:
                if int(combined_byte[i]) == 1:
                    print("На компараторе 2 достигнуло значение")
                if int(combined_byte[i]) == 0:
                    print("На компараторе 2 недостигнуло значение")

        # Переворачиваем байты для корректного отображения



        # Функция преобразования кода в напряжение
        voltage_1 = [0, 0]
        voltage_2 = [0, 0]
        # Принимаем пакет
        volt_1 = bytearray(data[1])[34:36]
        volt_2 = bytearray(data[1])[36:38]
        # Формируем правильный массив байт
        voltage_1[0] = int(volt_1[1])
        voltage_1[1] = int(volt_1[0])
        voltage_2[0] = int(volt_2[1])
        voltage_2[1] = int(volt_2[0])

        res_voltage_1 = convert_base(bytes(voltage_1).hex(), from_base=16, to_base=10)
        voltage_dac_1 = int(res_voltage_1)
        res_voltage_2 = convert_base(bytes(voltage_2).hex(), from_base=16, to_base=10)
        voltage_dac_2 = int(res_voltage_2)

        return [code_dac_1, code_dac_2, voltage_dac_1, voltage_dac_2]

