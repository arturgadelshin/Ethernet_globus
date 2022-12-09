from loggings import *
from globus_ethernet import *
from parsing_ethernet import *
import time
from base_interface_function import *
from special_interface_function import *
from GwInstek74303S.com_voltage_regulator import VoltageRegulator


class Stages_01():
    "Итерфейсный блок"
    pars = Parsing() # Создание объекта Парсера, для распарсивания принятых пакетов
    recieve_data = WindowParsing()

    def __init__(self):
        self.stage = 'Наименование проверки'
        self.name_stage = 'Проверка интерфесных фукнций'
        self.name_param_01 = 'Исходное Soft'
        self.name_param_02 = 'Исходное Hard'
        self.name_param_03 = 'Чтение тестовой информации без сброса'
        self.name_param_04 = 'Чтение тестовой информации со сбросом'
        self.state = [1, 1, 1, 1]  # Кол-во состояний равно кол-ву параметров
        #add_log_file(self.stage + ' - ' + self.name_stage)

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
        write = read_testinfo_and_rgsmk(1)  # Было так
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

    def parameter_01(self):
        must_be = ''
        write = smk('01')
        add_log_file(self.name_param_01)
        data = Ethernet().swap(write)
        self.pars.reg_state_packet(data[1])
        add_log_file(data[1])
        #valid = True
        recieve_data = data[1][21]    # Получаем статус команды
        if hex(recieve_data) == hex(0x02):  #[0x02] - из протокола проверки МКС команда в процессе выполнения
            valid_recieve = True
        else:
            valid_recieve = False
        write = data_request(0)
        add_log_file('Запрос данных')
        data = Ethernet().swap(write)
        recieve_data = data[1][2:4]
        if hex(recieve_data[0]) == hex(0x01):  # [0x01] - из протокола проверки МКС байт состояния
            valid_rg = True
        else:
            valid_rg = False
        msg = self.pars.reg_state_packet(data[1])
        add_log_file(msg)

        # Здесь добавить команду чтение тестовой информации и ее анализ
        write = read_testinfo_and_rgsmk(0)
        add_log_file('Чтение тестовой информации без сброса регистра СМК')
        data = Ethernet().swap(write)
        recieve_data = data[1][22:]
        add_log_file(recieve_data)

        # Здесь сделать анализ

        write = read_testinfo_and_rgsmk(1)
        add_log_file('Чтение тестовой информации со сбросом регистра СМК')
        data = Ethernet().swap(write)
        recieve_data = data[1][22:]
        add_log_file(recieve_data)

        # Здесь сделать анализ

        # Блок проверки
        if (valid_recieve is True) and (valid_rg is True):
            valid = True
            add_log_file(data[1])
        else:

            valid = False
            add_log_file('НГ', data[1])
        return [data, must_be, valid]


    def parameter_02(self, repeat):
        pass


class Stages_03:
    """ Проверка модуля в одиночном режиме """
    pars = Parsing()  # Создание объекта Парсера, для распарсивания принятых пакетов
    recieve_data = WindowParsing()
    voltage_1 = 2.0
    delta_1 = 10.0  # погрешность(%) в низу границы 2В
    voltage_2 = 16.0
    delta_2 = 7.0  # погрешность(%) в середине границы 17В
    voltage_3 = 30.0
    delta_3 = 5.0  # погрешность(%) в низу границы 30В
    count_channel_calibrate = 32  # Здесь должно быть 32 канала
    count_bytes_in_one_channel = 16

    def __init__(self):
        self.name_stage = 'Работа в одиночном режиме'
        self.name_param_01 = 'Уровень 2В'
        self.name_param_02 = 'Уровень 16В'
        self.name_param_03 = 'Уровень 30В'

    def search_error_em(self, name_param, count_channel_calibrate, voltage, step_voltage,
        number_of_successful_operations, delta_error):
        voltage_regulator = VoltageRegulator()  # Создать объект Regulator
        voltage_regulator.set_port()            # Задать порт
        levels = []
        compare = CompareLevel()

        # Здесь запросим коэффициенты полинома
        write = read_k_polinoms()  # Чтение коэффициентов полиномов
        Ethernet().swap(write)
        write = data_request(0)  # Запрос данных (калибровочных коэффициентов)
        data = Ethernet().swap(write)
        # 8 байт - Frame, 24 байта - любых см. команду write_k_polinoms()
        undefined_bytes = 24  # Было 24 - решил убрать для экономии памяти
        k_polinoms = data[1][22 + 8 + undefined_bytes:]
        k_polinoms = k_polinoms[0:self.count_channel_calibrate * self.count_bytes_in_one_channel]
        list_polinoms = []
        # Переложим коэффициенты k_polinoms в список списков для удобства работы
        for i in range(0, self.count_channel_calibrate):
            row_polinoms = []
            for j in range(0, self.count_bytes_in_one_channel):
                row_polinoms.append(k_polinoms[i * self.count_bytes_in_one_channel + j])
            list_polinoms.append(row_polinoms)
        valid = True
        # Должно быть с 0, поставил с 4 для отладки, так как кривые импульсы
        for channel in range(0, count_channel_calibrate, 4):
            # Для первого уровня
            up_voltage_1 = voltage + delta_error * voltage / 100
            down_voltage_1 = voltage - delta_error * voltage / 100
            count = 0

            # Вычислить откалиброванное напряжение
            args = list_polinoms[channel]
            y = -((int.from_bytes([args[1], args[0]], byteorder='big') / (10 ** 8)) * (float(voltage) ** 3)) + \
                (int.from_bytes([args[3], args[2]], byteorder='big') / (10 ** 6)) * (float(voltage) ** 2) - \
                (int.from_bytes([args[5], args[4]], byteorder='big') / (10 ** 5)) * float(voltage) + \
                (int.from_bytes([args[7], args[6]], byteorder='big') / (10 ** 3))
            if y < 0:
                add_log_file('НГ', f'Канал {channel}')
                continue
            voltage_calibrate = float(format(float(voltage) / y, '.2f'))
            channel_volt = {str(channel + 1): [voltage_calibrate, voltage_calibrate]}
            voltage_regulator.set_calibrate_voltage(up_voltage_1)  # Задаем напряжение на источнике
            while True:
                up_voltage_1 = round(up_voltage_1, 2)
                voltage_regulator.set_fast_voltage(up_voltage_1)  # Задаем напряжение на источнике
                logs = compare.compare_level(0, **channel_volt)  # Выполнение разового компарирования
                # Маска контролируемых каналов побитово
                int_mask_channels = round(2 ** int(channel))
                mask_channels = [0] * 4
                if int_mask_channels < 255:
                    mask_channels[0:4] = int_mask_channels, 0, 0, 0
                if 255 < int_mask_channels < 65535:
                    rez = int_mask_channels.to_bytes((int_mask_channels.bit_length() + 7) // 8, 'little')
                    mask_channels[0:4] = rez[0], rez[1], 0, 0
                if 65535 < int_mask_channels < 16777215:
                    rez = int_mask_channels.to_bytes((int_mask_channels.bit_length() + 7) // 8, 'little')
                    mask_channels[0:4] = rez[0], rez[1], rez[2], 0
                if 16777215 < int_mask_channels < 4294967295:
                    rez = int_mask_channels.to_bytes((int_mask_channels.bit_length() + 7) // 8, 'little')
                    mask_channels[0:4] = rez[0], rez[1], rez[2], rez[3]
                mask = [0]*4
                for i in range(0, 4):
                    mask[i] = logs[0][0][i] & mask_channels[i]
                if mask != mask_channels:
                    count += 1
                else:
                    count = 0
                    up_voltage_1 -= step_voltage

                if count == number_of_successful_operations:  # Количество успешных срабатываний подряд
                    add_log_file(f'Уровень 1 для {voltage}(В) срабатывания - на выключение канала {channel+1}'
                                 f' равен {up_voltage_1}(В)')
                    time.sleep(2.0)
                    break
                if up_voltage_1 <= down_voltage_1:
                    add_log_file(f'Уровень 1 для {voltage}(В) срабатывания - на включение канала {channel+1}'
                                 f' не найден')

                    add_log_file('НГ', f'Уровень 1 для {voltage}')
                    valid = False
                    time.sleep(2.0)
                    break

            # Для второго уровня
            up_voltage_2 = voltage + delta_error * voltage / 100
            down_voltage_2 = voltage - delta_error * voltage / 100  # Берем нижнюю границы от предыдущего поиска сделал для ускорения поиска
            count = 0
            voltage_regulator.set_calibrate_voltage(up_voltage_1)  # Задаем напряжение на источнике
            while True:
                down_voltage_2 = round(down_voltage_2, 2)
                voltage_regulator.set_fast_voltage(down_voltage_2)  # Задаем напряжение на источнике
                logs = compare.compare_level(0, **channel_volt)  # Выполнение разового компарирования
                # Маска контролируемых каналов побитово
                int_mask_channels = round(2 ** int(channel))
                mask_channels = [0] * 4
                if int_mask_channels < 255:
                    mask_channels[0:4] = int_mask_channels, 0, 0, 0
                if 255 < int_mask_channels < 65535:
                    rez = int_mask_channels.to_bytes((int_mask_channels.bit_length() + 7) // 8, 'little')
                    mask_channels[0:4] = rez[0], rez[1], 0, 0
                if 65535 < int_mask_channels < 16777215:
                    rez = int_mask_channels.to_bytes((int_mask_channels.bit_length() + 7) // 8, 'little')
                    mask_channels[0:4] = rez[0], rez[1], rez[2], 0
                if 16777215 < int_mask_channels < 4294967295:
                    rez = int_mask_channels.to_bytes((int_mask_channels.bit_length() + 7) // 8, 'little')
                    mask_channels[0:4] = rez[0], rez[1], rez[2], rez[3]
                mask = [0] * 4
                for i in range(0, 4):
                    mask[i] = logs[0][1][i] & mask_channels[i]
                if mask == mask_channels:
                    count += 1
                else:
                    count = 0
                    down_voltage_2 += step_voltage

                if count == number_of_successful_operations:  # Количество успешных срабатываний подряд
                    add_log_file(f'Уровень 2 для {voltage}(В) срабатывания - на включение канала {channel+1}'
                                 f' равен {down_voltage_2}(В)')
                    time.sleep(2.0)
                    break
                if down_voltage_2 >= up_voltage_2:
                    add_log_file(f'Уровень 2 для {voltage}(В) срабатывания - на включение канала {channel+1}'
                                 f' не найден')
                    add_log_file('НГ', f'Уровень 2 для {voltage}')
                    valid = False
                    time.sleep(2.0)
                    break

            delta = abs(up_voltage_1-down_voltage_2)  # Разница между верхним и нижним уровнем
            error_voltage = round((delta*100)/voltage, 2)  # Вычисление погрешности
            levels.append({str(channel+1): error_voltage})
            # Здесь сделать анализ

            if error_voltage > self.delta_1:
                valid = False
                add_log_file('НГ', name_param)
        voltage_regulator.port_close()  # Закрыть порт после всей проверки
        return [levels, valid]

    def parameter_01(self):
        """
        Здесь реализовать выдачу в ЦАП откалиброванных 2 вольт и
        изменение напряжения на источнике с шагом 50 мВ.
        Сделать маску на канал, будем ждать переключения канала
        :return:
        """

        step_voltage = 0.02  # 20 мВ шаг напряжения на источнике (на входе платы)
        number_of_successful_operations = 15  # Количество успешных срабатываний подряд
        rez = self.search_error_em(self.name_param_01, self.count_channel_calibrate,
                             self.voltage_1, step_voltage, number_of_successful_operations,
                             self.delta_1)
        return rez

    def parameter_02(self):
        """
        Здесь реализовать выдачу в ЦАП откалиброванных 16 вольт и
        изменение напряжения на источнике с шагом 50 мВ.
        Сделать маску на канал, будем ждать переключения канала
        :return:
        """

        step_voltage = 0.02  # 20 мВ шаг напряжения на источнике (на входе платы)
        number_of_successful_operations = 15  # Количество успешных срабатываний подряд
        rez = self.search_error_em(self.name_param_02, self.count_channel_calibrate,
                             self.voltage_2, step_voltage, number_of_successful_operations,
                             self.delta_2)
        return rez

    def parameter_03(self):
        """
        Здесь реализовать выдачу в ЦАП откалиброванных 30 вольт и
        изменение напряжения на источнике с шагом 50 мВ.
        Сделать маску на канал, будем ждать переключения канала
        :return:
        """

        step_voltage = 0.02  # 20 мВ шаг напряжения на источнике (на входе платы)
        number_of_successful_operations = 15  # Количество успешных срабатываний подряд
        rez = self.search_error_em(self.name_param_03, self.count_channel_calibrate,
                             self.voltage_3, step_voltage, number_of_successful_operations,
                             self.delta_3)
        return rez


class CompareLevel:

    def __init__(self):
        # Может сюда стоит добавить команду сброса soft ?
        ...

    def compare_level(self, mode, **kwargs):
        # Установка порогов и номера каналов которые контролируются побитово
        write = setting_for_work(mode, **kwargs)
        Ethernet().swap(write)
        # Программный запуск
        write = program_start()
        Ethernet().swap(write)
        time.sleep(0.01)
        if mode == 1:
            while True:
                # Запрос данных
                write = data_request(0)
                data = Ethernet().swap(write)
                logs = []
                # print(len(data[1]))
                if len(data[1]) > 32:
                    for i in range(0, int((len(data[1])-38)/16+1)):
                        # Формируем список принятых байтов
                        logs.append([data[1][30+(16*i):34+(16*i)], data[1][34+(16*i):38+(16*i)]])
                else:
                    logs = [[0x00.to_bytes(4, byteorder='big'), 0x00.to_bytes(4, byteorder='big')]]*38
                yr_1 = (bin(logs[-1][0][3])[2:])
                yr_2 = (bin(logs[-1][1][3])[2:])
                # time.sleep(0.001)
                print(yr_1, yr_2)
        else:
            # Запрос данных
            write = data_request(0)
            data = Ethernet().swap(write)
            logs = []
            # print(len(data[1]))
            if len(data[1]) > 32:
                for i in range(0, int((len(data[1]) - 38) / 16 + 1)):
                    # Формируем список принятых байтов
                    logs.append([data[1][30 + (16 * i):34 + (16 * i)], data[1][34 + (16 * i):38 + (16 * i)]])
            else:
                logs = [[0x00.to_bytes(4, byteorder='big'), 0x00.to_bytes(4, byteorder='big')]] * 38
        return logs
        # log_1 = data[1][30:34]
        # log_2 = data[1][34:38]
        # # Cброс
        # write = reset_em(0)
        # Ethernet().swap(write)


class Calibrate:
    """ Класс который описывает калибровку каждого канала """
    pars = Parsing()  # Создание объекта Парсера, для распарсивания принятых пакетов
    recieve_data = WindowParsing()
    compare = CompareLevel()

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
