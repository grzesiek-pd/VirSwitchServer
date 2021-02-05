import pickle
import socket as sock
import json
import subprocess
from subprocess import PIPE
from datetime import  datetime


def read_users_file():
    with open('vir_switch_server/users.json') as users_file:
        users = json.load(users_file)
        print(type(users))
        return users


def read_logs_file():
    f = open('vir_switch_server/logs.txt', 'r', encoding='utf-8')
    logs = f.readlines()
    f.close()
    return logs


def add_logs_entry(user, address, action):
    f = open('vir_switch_server/logs.txt', 'a+', encoding='utf-8')
    now = datetime.now()
    dt_string = now.strftime("%d/%m/%Y - %H:%M:%S")
    f.write(f'{dt_string} ----- FROM: {address[0]} ----- USER: {user} ----- ACTION: {action}\n')
    f.close()


def reset_logs():
    return


def control_vm(cmd):
    out = ''
    err = ''
    try:
        p = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True)
        stdout, stderr = p.communicate()

        out_raw = stdout.decode('utf-8')
        err = stderr.decode('utf-8')
        out = []
    except Exception as er:
        err = str(er)
        print(err)
        out = out_raw.split('\n')
    for line in out:
        print(type(line), line)
    return


def make_vm_list(cmd):
    out = ''
    err = ''
    try:
        p = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True)
        stdout, stderr = p.communicate()

        out = stdout.decode('utf-8')
        err = stderr.decode('utf-8')
        v_list = []
    except Exception as er:
        err = str(er)
    out_raw = out.split('\n')
    for line in out_raw[2:-2]:
        li = line.split()
        li.pop(0)
        if len(li) > 2:
            li[1] = li[1] + ' ' + li[2]
            li.pop(2)
        print(li)
        print(line)
        v_list.append(li)
    print(v_list)

    return v_list

