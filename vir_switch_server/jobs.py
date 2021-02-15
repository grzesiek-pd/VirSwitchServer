import subprocess
from subprocess import PIPE
from datetime import datetime
import sqlite3
import hashlib

c = sqlite3.connect('vir_switch_server/users.db')
cursor = c.cursor()


def create_table():
    init_pass = hashlib.md5(b'admin').hexdigest()
    query = f"CREATE TABLE IF NOT EXISTS users(login TEXT UNIQUE , password TEXT , admin TEXT , vms TEXT );"
    cursor.execute(query)
    query2 = f"SELECT login FROM users WHERE admin = 'yes';"
    cursor.execute(query2)
    admins = cursor.fetchall()
    c.commit()
    if len(admins) == 0:
        query2 = f"INSERT INTO users(login, password, admin, vms) VALUES ('admin','{init_pass}', 'yes', 'all');"
        cursor.execute(query2)
        c.commit()


def add_user(username, user_data):
    pass_hash = user_data[0]
    is_admin = user_data[1]
    vms = user_data[2]

    query = "INSERT INTO users(login, password, admin, vms) VALUES (?, ?, ?, ?);"
    cursor.execute(query, (username, pass_hash, is_admin, vms))
    c.commit()


def delete_user(username):
    query = f"DELETE FROM users WHERE login ='{username}';"
    cursor.execute(query)
    c.commit()


def check_user(username, password):
    query = f"SELECT login, password, admin, vms FROM users WHERE login = '{username}';"
    cursor.execute(query)
    check = cursor.fetchone()
    c.commit()
    if check:
        if password in check:
            user = check[0]
            is_admin = check[2]
            vms = check[3]
            msg = ['password_ok', user, 'pass', is_admin, vms]
            add_logs_entry(user, action=f'login to sever')
            return msg
        else:
            msg = ['password_wrong']
            return msg
    else:
        msg = ['password_wrong']
        return msg


def users_list():
    query = f"SELECT login, admin, vms FROM users ORDER BY admin DESC, login ASC ;"
    cursor.execute(query)
    u_list = cursor.fetchall()
    c.commit()
    return u_list


def read_logs_file():
    f = open('vir_switch_server/logs.txt', 'r', encoding='utf-8')
    logs = f.readlines()
    f.close()
    return logs


def add_logs_entry(user, action):
    f = open('vir_switch_server/logs.txt', 'a+', encoding='utf-8')
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y - %H:%M:%S")
    f.write(f'{dt_string} ----- USER: {user} ----- ACTION: {action}\n')
    f.close()


def reset_logs(user):
    f = open('vir_switch_server/logs.txt', 'w', encoding='utf-8')
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y - %H:%M:%S")
    f.write(f'{dt_string} --- CLEAR LOGS BY USER: {user}\n')
    f.close()


def control_vm(cmd):
    try:
        p = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True)
        stdout, stderr = p.communicate()
        out_raw = stdout.decode('utf-8')
        err = stderr.decode('utf-8')
    except Exception as er:
        err = str(er)
        print(err)
    out = out_raw.split()
    # print(out_raw)
    # print(out)
    return out


def make_vm_list(cmd):
    out = ''
    err = ''
    try:
        p = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True)
        stdout, stderr = p.communicate()
        out = stdout.decode('utf-8')
        err = stderr.decode('utf-8')
        v_list = []
        v_list_info = list()
    except Exception as er:
        err = str(er)
    out_raw = out.split('\n')
    for line in out_raw[2:-2]:
        li = line.split()
        # print(li)
        v_list_info.append(li[1])

    for vm in v_list_info:
        try:
            p = subprocess.Popen(f"echo 'gugugu' | sudo -S virsh dominfo {vm} | grep '\(State\|memory\|CPU\)'", stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True)
            stdout, stderr = p.communicate()

            out = stdout.decode('utf-8')
            err = stderr.decode('utf-8')
            info = []
        except Exception as er:
            err = str(er)
        out_raw = out[0:-2].split('\n')
        info.append(vm)
        state = out_raw[0].split()[-1]
        info.append(state)
        cpu = out_raw[1].split()[-1]
        info.append(cpu)
        max_memory = int(int(out_raw[-2].split()[-2]) / 1024)
        info.append(max_memory)
        memory = int(int(out_raw[-1].split()[-2]) / 1024)
        info.append(memory)
        # print(info)
        v_list.append(info)

    return v_list

