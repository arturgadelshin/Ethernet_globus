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
    # Зарезервированные и вроде как нерачие байты Атаманчук Ю.И сказал (УБРАЛ)
    undefined_bytes = [0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]*3  # Их получается 24 байта

    df = pd.read_excel('table_for_grafics.xlsx')
    data_table_calibrate = df.copy()
    data_1_channel = DataFrame()
    data_2_channel = DataFrame()
    data_3_channel = DataFrame()
    data_4_channel = DataFrame()
    data_5_channel = DataFrame()
    data_6_channel = DataFrame()
    data_7_channel = DataFrame()
    data_8_channel = DataFrame()
    data_9_channel = DataFrame()
    data_10_channel = DataFrame()
    data_11_channel = DataFrame()
    data_12_channel = DataFrame()
    data_13_channel = DataFrame()
    data_14_channel = DataFrame()
    data_15_channel = DataFrame()
    data_16_channel = DataFrame()
    data_17_channel = DataFrame()
    data_18_channel = DataFrame()
    data_19_channel = DataFrame()
    data_20_channel = DataFrame()
    data_21_channel = DataFrame()
    data_22_channel = DataFrame()
    data_23_channel = DataFrame()
    data_24_channel = DataFrame()
    data_25_channel = DataFrame()
    data_26_channel = DataFrame()
    data_27_channel = DataFrame()
    data_28_channel = DataFrame()
    data_29_channel = DataFrame()
    data_30_channel = DataFrame()
    data_31_channel = DataFrame()
    data_32_channel = DataFrame()

    count_step_voltage = 8
    count_channel = 32
    for i in range(0, count_step_voltage):
        data_1_channel = data_1_channel.append(
            ([data_table_calibrate['K_kalibrate'][i * count_channel]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_2_channel = data_2_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 1]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_3_channel = data_3_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 2]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_4_channel = data_4_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 3]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_5_channel = data_5_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 4]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_6_channel = data_6_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 5]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_7_channel = data_7_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 6]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_8_channel = data_8_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 7]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_9_channel = data_9_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 8]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_10_channel = data_10_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 9]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_11_channel = data_11_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 10]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_12_channel = data_12_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 11]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_13_channel = data_13_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 12]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_14_channel = data_14_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 13]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_15_channel = data_15_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 14]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_16_channel = data_16_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 15]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_17_channel = data_17_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 16]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_18_channel = data_18_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 17]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_19_channel = data_19_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 18]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_20_channel = data_20_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 19]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_21_channel = data_21_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 20]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_22_channel = data_22_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 21]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_23_channel = data_23_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 22]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_24_channel = data_24_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 23]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_25_channel = data_25_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 24]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_26_channel = data_26_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 25]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_27_channel = data_27_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 26]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_28_channel = data_28_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 27]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_29_channel = data_29_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 28]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_30_channel = data_30_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 29]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_31_channel = data_31_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 30]]), ignore_index=True)
    for i in range(0, count_step_voltage):
        data_32_channel = data_32_channel.append(
            ([data_table_calibrate['K_kalibrate'][(i * count_channel) + 31]]), ignore_index=True)

    volt = pd.unique(data_table_calibrate['Voltage'])
    voltage = DataFrame(volt, columns=['Voltage'])

    data = pd.concat([data_1_channel, data_2_channel, data_3_channel, data_4_channel,
                      data_5_channel, data_6_channel, data_7_channel, data_8_channel,
                      data_9_channel, data_10_channel, data_11_channel, data_12_channel,
                      data_13_channel, data_14_channel, data_15_channel, data_16_channel,
                      data_17_channel, data_18_channel, data_19_channel, data_20_channel,
                      data_21_channel, data_22_channel, data_23_channel, data_24_channel,
                      data_25_channel, data_26_channel, data_27_channel, data_28_channel,
                      data_29_channel, data_30_channel, data_31_channel, data_32_channel,
                      voltage], axis=1)
    data = data.set_index('Voltage')
    writer = pd.ExcelWriter('table_for_kalibrates.xlsx')
    data.to_excel(writer, 'Sheet1')
    writer.save()
    df = pd.read_excel('table_for_kalibrates.xlsx')

    index_polinoms = ['a', 'b', 'c', 'd']
    # Нужно чтобы переименовать столбцы по-новому для удобства работы с ними
    for i, name in enumerate(df.columns):
        if i < 32:
            df.rename(columns={df.columns[i + 1]: i + 1}, inplace=True)
        else:
            break

    massive_k_polinoms = []
    list_voltage = array(df['Voltage'].values.tolist())  # Получаем столбец с напряжением

    def mapping(values_x, a, b, c, d):
        return a * values_x ** 3 + b * values_x ** 2 + c * values_x + d

    # Создадим пустой словарь
    list_channel = []
    for i in range(1, 33):
        list_channel.append(f'channel_{i}')

    dict_channel = dict.fromkeys(list_channel)
    for i in range(1, len(df.columns)):
        list_k_kalibrate = array(df[i].values.tolist())  # Получаем столбец с коэффициентами
        args, _ = curve_fit(mapping, list_voltage, list_k_kalibrate, method='lm')
        # print("Arguments: ", args)
        # Создаем список с отмасштабируемыми целыми коэффициентами
        int_args = [abs(round(args[0] * 10 ** 8)),  # 10^8
                    abs(round(args[1] * 10 ** 6)),  # 10^6
                    abs(round(args[2] * 10 ** 5)),  # 10^5
                    abs(round(args[3] * 10 ** 3))]  # 10^3

        dict_channel[f'channel_{i}'] = pd.Series(args, index=index_polinoms)  # Подсовываем коэффициенты полинома

        # Укладываем коэффициенты по логике: младший байт вперед
        for i in range(0, len(int_args)):
            if int_args[i] < 255:
                massive_k_polinoms.append(int_args[i])
                massive_k_polinoms.append(0)
            else:
                rez = int_args[i].to_bytes((int_args[i].bit_length() + 7) // 8, 'big')
                massive_k_polinoms.append(rez[1])
                massive_k_polinoms.append(rez[0])

        # Дозаполняем нулями, потом на их место допишем коэффициенты при температуре
        for i in range(0, 8):
            massive_k_polinoms.append(0)

        df_k_polinoms = pd.DataFrame(dict_channel)  # Создание DataFrame с коэффициентами полинома
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