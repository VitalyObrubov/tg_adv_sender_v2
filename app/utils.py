
def check_shedule(crontab_string: str) -> str:
    res = ''
    if crontab_string:
        crontab_lst = crontab_string.split()
    else:
        res = '<b>Неверная строка расписания</b>'
    if len(crontab_lst) !=5:
        res = '<b>В строке расписания должно быть 5 параметров</b>'

    return res