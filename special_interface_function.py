import pandas as pd
from scipy.optimize import curve_fit
from numpy import array, exp
from pandas.core.api import DataFrame

# Здесь будут отписаны все специальные интерфейсные функции

"""
Специальные интерфейсные функции разрабатываются в дополнение к
базовым функциям под конкретные ЭМ.
Коды команд для специальных интерфейсных функций должны быть
отражены в КД и/или ПД на конкретный ЭМ.
Коды команд выбираются последовательно из диапазона 0х80…0xFF.
"""


def calibrate(step, vector, channel):
    code_command = [0x80]
    reserved = [0x00]
    data = [step, vector]

    if channel < 255:
        data.append(channel)
        data.append(0)
    else:
        rez = channel.to_bytes((channel.bit_length() + 7) // 8, 'big')
        data.append(rez[1])
        data.append(rez[0])
    msg = (code_command + reserved + data)
    return bytes(msg)


def write_k_polinoms(*args):
    code_command = [0x83]
    reserved = [0x00]
    # Зарезервированные и вроде как нерабочие байты Атаманчук Ю.И сказал (УБРАЛ)
    undefined_bytes = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF] * 3  # Их получается 24 байта

    df = pd.read_excel('table_for_grafics.xlsx')
    index_polinoms = ['a', 'b', 'c', 'd']
    massive_k_polinoms = []
    # Получаем столбец с напряжением
    list_voltage = array(df['Voltage'].values.tolist())

    def mapping(values_x, a, b, c, d):
        return a * values_x ** 3 + b * values_x ** 2 + c * values_x + d

    name_channels = df.columns[2:].tolist()
    list_k_1 = []
    list_k_2 = []
    for i, name in enumerate(name_channels):
        if i % 2 == 0:
            list_k_1.append(name)
        else:
            list_k_2.append(name)

    dict_k_1 = {}
    dict_k_2 = {}

    for i, name_column in enumerate(list_k_1):
        list_k_kalibrate_1 = array(df[name_column].values.tolist())  # Получаем столбец с коэффициентами
        args_1, _ = curve_fit(mapping, list_voltage, list_k_kalibrate_1, method='lm')

        # Создаем список с отмасштабируемыми целыми коэффициентами
        map_args_1 = [round(args_1[0] * 10 ** 8),  # 10^8
                      round(args_1[1] * 10 ** 6),  # 10^6
                      round(args_1[2] * 10 ** 5),  # 10^5
                      round(args_1[3] * 10 ** 3)]  # 10^3

        dict_k_1[f'channel_k1_ch_{i}'] = pd.Series(args_1, index=index_polinoms)  # Подсовываем коэффициенты полинома

        for arg in map_args_1:
            number_bytes = arg.to_bytes(4, byteorder='little', signed=True)
            # Укладываем коэффициенты по логике - младший байт вперед
            for num in number_bytes:
                massive_k_polinoms.append(num)
        # Дозаполняем нулями, потом на их место допишем коэффициенты при температуре
        for j in range(0, 4):
            massive_k_polinoms.append(0)

    for i, name_column in enumerate(list_k_2):
        list_k_kalibrate_2 = array(df[name_column].values.tolist())  # Получаем столбец с коэффициентами
        args_2, _ = curve_fit(mapping, list_voltage, list_k_kalibrate_2, method='lm')
        # print("Arguments: ", args)

        # Создаем список с масштабируемыми целыми коэффициентами
        map_args_2 = [round(args_2[0] * 10 ** 8),  # 10^8
                      round(args_2[1] * 10 ** 6),  # 10^6
                      round(args_2[2] * 10 ** 5),  # 10^5
                      round(args_2[3] * 10 ** 3)]  # 10^3

        dict_k_2[f'channel_k2_ch_{i}'] = pd.Series(args_2, index=index_polinoms)
        # Укладываем коэффициенты по логике - младший байт вперед
        for arg in map_args_2:
            number_bytes = arg.to_bytes(4, byteorder='little', signed=True)
            # Укладываем коэффициенты по логике - младший байт вперед
            for num in number_bytes:
                massive_k_polinoms.append(num)
        # Дозаполняем нулями, потом на их место допишем коэффициенты при температуре
        for j in range(0, 4):
            massive_k_polinoms.append(0)

    dict_k = {**dict_k_1, ** dict_k_2}
    df_k_polinoms = pd.DataFrame(dict_k)  # Создание DataFrame с коэффициентами полинома
    writer = pd.ExcelWriter('table_k_polinoms.xlsx')
    df_k_polinoms.to_excel(writer, 'Sheet1')
    writer.save()
    msg = (code_command + reserved + undefined_bytes + massive_k_polinoms)
    return bytes(msg)


def read_k_polinoms():
    code_command = [0x84]
    reserved = [0x00]
    msg = (code_command + reserved)
    return bytes(msg)


def request_temperature():
    code_command = [0x82]
    reserved = [0x00]
    msg = (code_command + reserved)
    return bytes(msg)
