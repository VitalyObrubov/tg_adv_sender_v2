
def check_shedule(schedule: list) -> str:
    res = ''
    return res
    for time in schedule:       
        try:
            hours, mins = time.split(':')
            hours = int(hours)
            mins = int(mins)
            if hours < 0 or hours > 23 or mins < 0 or mins > 59:
                res += f'{time}, '
        except:
            res += f'{time}, '
    
    if res:
        res = 'Неверное время: ' + res
    return res