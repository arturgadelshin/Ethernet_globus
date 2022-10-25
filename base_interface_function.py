import struct
import re
import pandas as pd
from scipy.optimize import curve_fit
from numpy import array, exp
# Здесь будут отписаны все базовые интерфейсные функции

"""
Бит	Наименование поля	Описание
7	Тип команды	        0 – базовые функции
                        1 – специальные функции
0…6	Номер команды	    Произвольный номер команды
"""


def reset_em(add_bit):
    code_command = [0x01]
    reserved = [0x00]
    if add_bit == 1:
        add_byte = [0x01]
    else:
        add_byte = [0x00]
    msg = (code_command + reserved + add_byte)
    return bytes(msg)

"""
Команда «Исходное» (0х01 ).
команда предназначена для приведения ЭМ в исходное состояние
(алгоритм приведения и параметры исходного состояния определяются КД и/или ПД на конкретный ЭМ).
Команда передаётся с дополнительным байтом (младший бит: 1 – ЭМ выполняет переход на код загрузки,
т.е. аналогично аппаратному сбросу; 0 – ЭМ выполняет приведение в исходное состояние
функциональных узлов и буфера Ethernet).
"""


def read_testinfo_and_rgsmk(add_bit):
    code_command = [0x02]
    reserved = [0x00]
    if add_bit == 1:  # Сбросить регистр после ответа
        add_byte = [0x01]
    else:
        add_byte = [0x00]  # Не изменять значение регистра
    msg = (code_command + reserved + add_byte)
    return bytes(msg)


"""
На данную команду ЭМ отвечает укладывает в буфер пакетом данных, 
содержащимй регистр самоконтроля (32 байта), маску допустимых 
команд, контрольную сумму и версию встроенного ПО, частоту 
кварца (гене-ратора) и частоту ядра.
Команда может использоваться для получения результата самоконтроля,
проведенного при начальном запуске ЭМ или по команде 
«Самоконтроль».
Команда передаётся с дополнительным байтом
данных (младший бит: 0 –не изменять значение РгСМК, 
1 – сбросить после ответа).
"""


def replace_ip(s):
    code_command = [0x03]
    reserved = [0x00]
    # Длина адреса 4 байта
    addr_IP = s.split('.')
    data = []

    for i in addr_IP:
        data.append(int(i))

    msg = (code_command + reserved + data)
    return bytes(msg)

"""
Команда предназначена для смены IP адреса модуля по интерфейсу Ethernet.
Область данных команды включает 4 байта данных с новым IP адресом ЭМ.
Корректность смены IP-адреса проверяется последующим обращением к
модулю по новому IP-адресу (например, командой «Запрос данных»).
"""


def data_request(add_bit):
    code_command = [0x04]
    reserved = [0x00]
    if add_bit == 1:  # Вернуть самые свежие данные без удаления из буфера
        add_byte = [0x01]
    else:
        add_byte = [0x00]  # Вернуть самые ранние данные с удалением их из буфера
    msg = code_command + reserved + add_byte
    return bytes(msg)


"""
Команда служит для чтения данных из выходного буфера Ethernet.
На данную команду ЭМ отвечает пакетом, содержащим самый ранний 
(или наоборот самый поздний) элемент в буфере Ethernet.
Формат представления данных определяется в КД и/или ПД 
на конкретный ЭМ.
Команда передаётся с дополнительным байтом данных 
(младший бит: 0 – вернуть самые ранние данные с удалением 
их из буфера, 1 – вернуть самые свежие данные без удаления
 из буфера)
"""


def read_data_any_addr(addr_read_data, size_data):
    code_command = [0x05]
    reserved = [0x00]
    # Адрес считывания данных (4байта)
    # Максимальный размер запрашиваемых данных в байтах (2 байта)
    size = []

    data = []
    size_d = re.findall(r'\w\w', size_data)
    addr = re.findall(r'\w\w', addr_read_data)

    for i in addr:
        data.append(int(i, 16))

    for i in size_d:
        size.append((int(i)))
    # msg = bytes(code_command + reserved + data + size)
    msg = (code_command + reserved + data + size)
    return bytes(msg)


"""
Команда служит для чтения данных из произвольной области данных
(в том числе из регистров микроконтроллера).
Область данных команды включает 6 байт данных, обозначающих адрес
считывания данных (4 байта) и максимальный размер запрашиваемых 
данных в байтах (2 байта).
3.8.3.	На данную команду ЭМ формирует в буфере Ethernet пакет,
 содержащий запрашиваемый объем данных.
"""


def write_data_any_addr(addr_write_data, len_data, write_data):
    code_command = [0x06]
    reserved = [0x00]
    addr = []
    len_ = []
    data = []
    addr_d = re.findall(r'\w\w', addr_write_data)
    len_d = re.findall(r'\w\w', len_data)
    data_d = re.findall(r'\w\w', write_data)

    for i in addr_d:
        addr.append(int(i, 16))
    for i in len_d:
        len_.append(int(i, 16))
    for i in data_d:
        data.append(int(i, 16))

    msg = (code_command + reserved + addr + len_ + data)
    return bytes(msg)


"""
Команда служит для записи данных в произвольную область данных
(в том числе в регистры микроконтроллера).
Структура области данных команды приведена в таблице (Таблица 3.2).
Таблица 3.2 Структура области данных команды записи данных
Байты 	Наименование 	Описание
данных      поля
0…3	     Адрес	        Адрес, по которому записываются данные
4…5	     Длина	        Размер передаваемых данных, в бай-тах
6…N+5	 Данные	        Записываемые данные, N байт
"""


def write_32_bit_mask(addr_write_data, mask, write_data):
    code_command = [0x07]
    reserved = [0x00]
    addr = []
    mask_ = []
    data = []

    addr_d = re.findall(r'\w\w', addr_write_data)
    mask_d = re.findall(r'\w\w', mask)
    data_d = re.findall(r'\w\w', write_data)

    for i in addr_d:
        addr.append(int(i, 16))
    for i in mask_d:
        mask_.append(int(i, 16))
    for i in data_d:
        data.append(int(i, 16))

    msg = (code_command + reserved + addr + mask_ + data)
    return bytes(msg)


"""
Команда служит для записи данных в произвольную область данных с адресом,
выровненным на границу 4х байт (в том числе в регистры микроконтроллера).
При выполнении команды происходит считывание данных, маскирование 
изменяемых битов, запись данных в изменяемые биты и запись нового 
слова по тому же адресу.
Структура области данных команды приведена в таблице (Таблица 3.3).

3.10.4.	На данную команду ЭМ формирует ответ, 
содержащий новое значение 32х битного слова.

Таблица 3.3 Структура области данных команды записи данных по маске
Байты 	Наименование 	Описание
данных      поля
0…3	        Адрес	    Адрес, по которому записываются данные
4…7	        Маска	    Изменяемые биты
8…11	    Данные	    Записываемые данные, 4 байта
"""


def stop():
    code_command = [0x08]
    reserved = [0x00]
    msg = (code_command + reserved)
    return bytes(msg)


"""
Команда "Остановить" предназначена для прерывания выполняемых команд в ЭМ.
Команда передаётся без дополнительных данных.
"""


def reset_reg_state(mask):
    code_command = [0x09]
    reserved = [0x00]
    mask_ = []

    mask_d = re.findall(r'\w\w', mask)
    for i in mask_d:
        mask_.append(int(i, 16))

    msg = (code_command + reserved + mask_)
    return bytes(msg)

"""
Команда предназначена для сброса бит регистра состояния.
В области данных передаётся маска бит, которые необходимо 
сбросить (Таблица 2.4).
На данную команду ЭМ отвечает пакетом данных, с обновленным 
регистром состояния.
"""


def program_start():
    code_command = [0x10]
    reserved = [0x00]
    msg = (code_command + reserved)
    return bytes(msg)

"""
Команда предназначена для программного запуска ЭМ, 
согласно ранее заданным установкам (в соответствии с КД и/
или ПД на конкретный ЭМ).
Команда реализуется в ЭМ, в которых предусмотрен программный 
запуск (для остальных ЭМ – невыполняемая команда, Таблица 2.6).
Команда передаётся без дополнительных данных.
"""


def setting_em(mask, write_data):
    code_command = [0x11]
    reserved = [0x00]
    mask_ = []
    data = []

    mask_d = re.findall(r'\w\w', mask)
    data_d = re.findall(r'\w\w', write_data)

    for i in mask_d:
        mask_.append(int(i, 16))
    for i in data_d:
        data.append(int(i, 16))

    msg = (code_command + reserved + mask_ + data)
    return bytes(msg)


"""
Команда настройки ЭМ предназначена для управления 
программно-управляемыми характеристиками ЭМ и реализуется в ЭМ в 
случае наличия программно-управляемых характеристик 
(для остальных ЭМ – невыпол-няемая команда, Таблица 2.6).

В области данных передаются параметры настройки. Сначала записывается 
маска настраиваемых параметров, потом сами параметры. 
Структура байта управления таймером и приоритетом приведена в таблице 
(Таблица 3.4). Состав, порядок, количество и размер остальных данных, 
передаваемых ЭМ зависит от количества программно-управляемых характеристик и опреде-ляется в ПД на конкретный ЭМ. Также программно-управляемыми характери-стиками являются выбор источника запуска или причина выдачи сигнала на триггерную линию «Запуск».

Таблица 3.4 Структура байта управления таймером и приоритетом
Биты	Наименование поля	Описание
7	        Резерв	        Резерв маски
6…4	        Маска	        Маска для бит 0…2
3	        Резерв	        Резерв команд
2	        Приоритет       «1» - приоритет интерфейсной команды
	        запуска         над триггерной линией Tr2,
            таймера         «0» - приоритет триггерной линии Tr2
1	        Запуск/Сброс	«1» - запуск таймера, 
                            «0» - сброс таймера в начальное состояние
0	        Источник	Выбор источника тактирования:
                        «0» - внутренний;
                        «1» - внешний.
Рекомендуется все настраиваемые характеристики передавать одной командой.
Факт успешного завершения ЭМ выполнения настройки определяется по 
установленному в «1» биту «READY».
"""


def smk(write_data):
    code_command = [0x0C]
    reserved = [0x00]
    data = []

    data_d = re.findall(r'\w\w', write_data)
    for i in data_d:
        data.append(int(i, 16))

    msg = (code_command + reserved + data)
    return bytes(msg)


"""
Команда предназначена для запуска встроенного самоконтроля ЭМ 
(алгоритм самоконтроля определяется КД и/или ПД на конкретный ЭМ).
В области данных команды передаются дополнительные параметры, 
необходимые для проведения самоконтроля. Размер и структура данных
определяется ПД на конкретный ЭМ. Рекомендуется в области данных 
команды использовать код для запуска конкретной функциональной группы 
общего самоконтроля или набора функциональных групп. 
Функциональные группы общего самоконтроля согласно ПД на модули. 
Например, если самоконтроль включает проверку 2 ОЗУ и одного таймера,
то с помощью дополни-тельных данных должна быть возможности провести 
самоконтроль одной ОЗУ либо 2-х ОЗУ либо только таймера и т.д.

Факт завершения ЭМ встроенного самоконтроля определяется по 
установленному в «1» биту «READY» (полученному, например, 
командой «Запрос данных»).
Коды команд 0х0D…0x7F зарезервированы для возможного наращивания 
перечня базовых функций.
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
    df = pd.read_excel('table_for_grafics_new.xlsx')
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
        int_args = [abs(int(args[0] * 10 ** 8)),  # 10^8
                    abs(int(args[1] * 10 ** 6)),  # 10^6
                    abs(int(args[2] * 10 ** 5)),  # 10^5
                    abs(int(args[3] * 10 ** 3))]  # 10^3

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


def read_k_kalibrate():
    code_command = [0x84]
    reserved = [0x00]
    msg = (code_command + reserved)
    return bytes(msg)
