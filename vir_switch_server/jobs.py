import subprocess
from subprocess import PIPE
from datetime import datetime
import sqlite3
import hashlib

c = sqlite3.connect('users.db')
cursor = c.cursor()
PREFIX = 'echo "gugugu" | sudo -S virsh '


def create_table():
    init_pass = hashlib.md5(b'admin').hexdigest()
    query = f"CREATE TABLE IF NOT EXISTS users(login TEXT , password TEXT , admin TEXT , vms TEXT );"
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


def update_user_vm_list(username, vm, action):
    query = f"SELECT vms FROM users WHERE login = '{username}';"
    cursor.execute(query)
    vms_tuple = cursor.fetchone()
    c.commit()
    vm_list = []
    try:
        vm_list = list(vms_tuple)[0].split(",")
        print(type(vm_list), vm_list)
    except TypeError as err:
        print(err)
    if action == 'remove':
        try:
            vm_list.remove(vm)
        except ValueError as err:
            print(err)
    elif action == 'add':
        vm_list.append(vm)

    vms_set = set(vm_list)
    vms = ",".join(vms_set)

    query = f"UPDATE users SET vms = '{vms}' WHERE login = '{username}';"
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
            add_logs_entry(user, action=f'login to server')
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
    print("user list: ", type(u_list), u_list)
    c.commit()
    return u_list


def read_logs_file():
    f = open('logs.txt', 'r', encoding='utf-8')
    logs = f.readlines()
    f.close()
    return logs


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
            p = subprocess.Popen(f'{PREFIX} dominfo {vm} | grep "\(State\|memory\|CPU\)"', stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True)
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

        try:
            p = subprocess.Popen(f'{PREFIX} domifaddr {vm}', stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True)
            stdout, stderr = p.communicate()

            out_ip = stdout.decode('utf-8')
            err_ip = stderr.decode('utf-8')

        except Exception as er:
            err_ip = str(err_ip)

        out_raw = out_ip.split('\n')
        print(out_raw)
        print(err_ip)
        # vm_ip_line = out_raw[2].split(' ')
        # print(vm_ip_line)
        # vm_ip = vm_ip_line[4]
        # info.append(vm_ip)

        try:
            p = subprocess.Popen(f'{PREFIX} desc {vm}', stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True)
            stdout, stderr = p.communicate()

            vm_description_str = stdout.decode('utf-8')
            err2 = stderr.decode('utf-8')

            if vm_description_str.startswith('No'):
                description_ip = "No description!"
                description_pwd = "No description!"
            else:
                desc_dict = eval(vm_description_str)
                # print(type(desc_dict), desc_dict)
                description_ip = desc_dict["ip"]
                description_pwd = desc_dict["root_pwd"]
                # print("ip:", desc_dict["ip"])
                # print("pass:", desc_dict["root_pwd"])

            # info = []
        except Exception as er:
            err2 = str(er)

        # print("ok->", description_ip, description_pwd)
        info.append(description_ip)
        info.append(description_pwd)
        v_list.append(info)

    return v_list


def update_description(data2, data3):
    vm = data2
    vm_ip = data3.get('ip')
    vm_pass = data3.get('pass')
    # out = ''
    # err = ''
    try:
        p = subprocess.Popen(f'{PREFIX} desc {vm} --new-desc ' +
                             "'{" + f'"ip": "{vm_ip}", "root_pwd": "{vm_pass}"'+"}'", stdout=PIPE, stderr=PIPE, stdin=PIPE,
                             shell=True)
        stdout, stderr = p.communicate()

        vm_description_str = stdout.decode('utf-8')
        err = stderr.decode('utf-8')

    except Exception as er:
        err = str(er)
        print(vm_description_str)
        print(err)
        print(er)

    return None


