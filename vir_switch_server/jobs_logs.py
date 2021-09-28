from datetime import datetime


def add_logs_entry(user, action):
    f = open('logs.txt', 'a+', encoding='utf-8')
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y/%H:%M:%S")
    f.write(f'{dt_string} user:{user} {action}\n')
    f.close()


def reset_logs(user):
    f = open('logs.txt', 'w', encoding='utf-8')
    now = datetime.now()
    dt_string = now.strftime("%d-%m-%Y/%H:%M:%S")
    f.write(f'{dt_string} clear logs by user: {user}\n')
    print(f'reset logs by: {user}')
    f.close()


def read_logs(page):
    f = open('logs.txt', 'r', encoding='utf-8')
    all_logs = f.readlines()
    lines = len(all_logs)
    if lines < 25:
        logs = {
            'prev': -1,
            'next': -1,
            'current': 1,
            'log_pack': all_logs
        }
    else:
        if page == 1:
            max = page * 25
            logs = {
                'prev': -1,
                'next': page + 1,
                'current': page,
                'log_pack': all_logs[0:max]
            }
        elif 1 < page <= lines/25:
            min = (page-1) * 25
            max = page * 25
            logs = {
                'prev': page - 1,
                'next': page + 1,
                'current': page,
                'log_pack': all_logs[min:max]
            }
        else:
            min = (page - 1) * 25
            logs = {
                'prev': page - 1,
                'next': -1,
                'current': page,
                'log_pack': all_logs[min:]
            }
    print(f'read logs')
    f.close()
    return logs



