from base_interface_function import*
from logging import *
from globus_ethernet import *
from parsing_ethernet import *
import time
from GUI.gui import *



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
        return [data, must_be]

    def parameter_02(self):
        write = reset_em(1)
        add_log_file(self.name_param_02)
        data = Ethernet().delay_swap(write)
        self.pars.info_packet(data[1])
        add_log_file(data[1])
        must_be = ''
        return [data, must_be]

    def parameter_03(self):
        write = read_testinfo_and_rgsmk(0)
        add_log_file(self.name_param_03)
        data = Ethernet().swap(write)
        self.pars.info_packet(data[1])
        add_log_file(data[1])
        must_be = ''
        return [data, must_be]

    def parameter_04(self):
        write = read_testinfo_and_rgsmk(1) # Было так
        add_log_file(self.name_param_04)
        data = Ethernet().swap(write)
        self.pars.info_packet(data[1])
        add_log_file(data[1])
        must_be = ''
        return [data, must_be]

    def all_parameters(self):
        self.parameter_01()
        self.parameter_02()
        self.parameter_03()
        self.parameter_04()


class Stage_02:
    "Блок с IP адресом"
    def __init__(self):
        self.name_stage = 'Проверка работы с IP адресом'
        add_log_file(self.name_stage)

    def parameter_01(self,IP):
        self.name_param_01 = 'Смена IP адреса'
        write = replace_ip(IP)
        add_log_file(self.name_param_01)
        data = Ethernet().swap(write)
        self.pars.info_parsing_packet(data[0])
        add_log_file(data)

    def parameter_02(self, repeat):
        pass



#eth = Ethernet('192.168.0.1', 1233)


# Между параметрами делать задержку в 3 секунды
# f.parameter_01()
# time.sleep(3)
# f.parameter_01()
# time.sleep(3)


#f.all_parameters()


