import socket as sock
import os
import sys

import jobs
from encrypt import Crypt

euid = os.geteuid()
if euid != 0:
    print("Application not started as root. Running sudo..")
    args = ['sudo', sys.executable] + sys.argv + [os.environ]
    os.execlpe('sudo', *args)

# start db with admin/admin
jobs.create_table()


def get_ip():
    s = sock.socket(sock.AF_INET, sock.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP


HOST = get_ip()
HOSTNAME = sock.gethostname()
PORT = 3333

if __name__ == '__main__':
    print(f'\033[92m start server({HOSTNAME}) at {HOST} / {PORT} (Ctrl-C to stop application)')

server_socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(10)


def vm_list():
    vm_list = jobs.make_vm_list(f'virsh list --all ')
    return vm_list


while True:
    client_socket, address = server_socket.accept()
    data_from = client_socket.recv(8000)

    if data_from:
        try:
            data_pack = Crypt.decrypt(data_from)
            # received pack view
            # print(f'-------------------')
            # print(f'otrzymana paczka -> {type(data_from)}--{data_from}')
            # print(f'rozkodowana paczka -> {type(data_pack)}--{data_pack}')

            if len(data_pack) == 4:
                msg_id = data_pack[0]
                a_user = data_pack[1]
                data2 = data_pack[2]
                data3 = data_pack[3]
            else:
                msg_id = 'error'

        except Exception as er:
            err = str(er)
            print(err)
            print(f'\033[91m z adresu: {address}')
            print("otrzymany pakiet binarny: ", data_from)

        # comm check
        # print(f"Uzyskano połączenie od hosta {address[0]} na porcie: {address[1]} wiadomość: {data_pack}")

        if msg_id == "user_check":
            msg_to_send = jobs.check_user(a_user, data3)

        elif msg_id == "get_user_list":
            msg_to_send = jobs.users_list()

        elif msg_id == "error":
            msg_to_send = "error"

        elif msg_id == "add_user":
            jobs.add_user(a_user, data2)
            msg_to_send = jobs.users_list()

        elif msg_id == "update_user_vm_list":
            jobs.update_user_vm_list(a_user, data2, data3)
            msg_to_send = jobs.users_list()

        elif msg_id == "delete_user":
            jobs.delete_user(a_user)
            msg_to_send = jobs.users_list()

        elif msg_id == "host_memory":
            host = jobs.control_vm(f'free -m| grep Pam')
            msg_to_send = host

        elif msg_id == "v_list":
            v_list = jobs.make_vm_list(f'virsh list --all ')
            msg_to_send = v_list

        elif msg_id == "get_logs":
            logs = jobs.read_logs(data2)
            msg_to_send = logs

        elif msg_id == "reset_logs":
            logs = jobs.reset_logs(a_user)
            msg_to_send = logs

        elif msg_id == "get_vm_details":
            vm_details = jobs.make_vm_details(data2)
            msg_to_send = vm_details

        elif msg_id == "update_description":
            vm_details = jobs.update_description(data2, data3)
            msg_to_send = vm_list()
# memory
        elif msg_id == "new_memory":
            jobs.control_vm(f'virsh setmem {data2} {data3}M')
            jobs.add_logs_entry(a_user, action=f'set memory {data2}: {data3} MB')
            print(f'user: {a_user} set memory {data2}: {data3} MB')
            msg_to_send = vm_list()

        elif msg_id == "new_max_memory":
            jobs.control_vm(f'virsh setmaxmem {data2} {data3}M')
            jobs.add_logs_entry(a_user, action=f'set max memory {data2}: {data3} MB')
            print(f'user: {a_user} set max memory {data2}: {data3} MB')
            msg_to_send = vm_list()

        elif msg_id == "new_cpus":
            jobs.control_vm(f'virsh setvcpus {data2} {data3} --config --maximum')
            jobs.control_vm(f'virsh setvcpus {data2} {data3} --config')
            jobs.add_logs_entry(a_user, action=f'set cpus {data2}: {data3}')
            print(f'user: {a_user} set cpus {data2}: {data3}')
            msg_to_send = vm_list()

        elif msg_id == "start":
            jobs.control_vm(f'virsh start {data2} ')
            jobs.add_logs_entry(a_user, action=f'start {data2}')
            print(f'user: {a_user} start {data2}')
            msg_to_send = vm_list()

        elif msg_id == "stop":
            jobs.control_vm(f'virsh shutdown {data2} ')
            jobs.add_logs_entry(a_user, action=f'stop {data2}')
            print(f'user: {a_user} stop {data2}')
            msg_to_send = vm_list()

        elif msg_id == "restart":
            jobs.control_vm(f'virsh reboot {data2} ')
            jobs.add_logs_entry(a_user, action=f'reboot {data2}')
            print(f'user: {a_user} reboot {data2}')
            msg_to_send = vm_list()

        elif msg_id == "kill":
            jobs.control_vm(f'virsh destroy {data2} ')
            jobs.add_logs_entry(a_user, action=f'force stop {data2}')
            print(f'user: {a_user} force stop {data2}')
            msg_to_send = vm_list()

        else:
            msg_to_send = ['password_wrong']

        pack_to_send = Crypt.encrypt(msg_to_send)
        try:
            client_socket.send(pack_to_send)
        except ConnectionError as err:
            print(err)

        # send pack view
        # print(f'-------------------')
        # print(f'przygotowana paczka -> {type(msg_to_send)}--{msg_to_send}')
        # print(f'zakodowana paczka -> {type(pack_to_send)}--{pack_to_send}')

    else:
        print("<<< otrzymano pusty pakiet >>>")





