import datetime


def control_check():
    pass


def clear_log_file():
    with open("log.txt", "w") as f:
        f.close()


def add_log_file(*args):
    with open("log.txt", "at") as f:
        lst = []
        runtime = str(datetime.datetime.now())
        lst.append(runtime)
        lst.append(str(args))
        # for arg in args:
        #     lst.append(arg)
        print(lst, file=f)


class LogFile:
    """ Собственный класс для логгирования работы программы """
    def __init__(self):
        with open("log.txt", "wt") as f:
           f.close()

    def add_log(self, *args):
        with open("log.txt", "at") as f:
            lst = []
            runtime = str(datetime.datetime.now())
            lst.append(runtime)
            lst.append(str(args))
            # for arg in args:
            #     lst.append(arg)
            print(lst, file=f)
            f.close()


class LogInfo:
    def __init__(self):
        pass


class LogCheck:
    def __init__(self):
        pass
