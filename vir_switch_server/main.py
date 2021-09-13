import socket as sock
import jobs
from vir_switch_server.encrypt import Crypt

HOST = '192.168.81.131'
PORT = 3333
jobs.create_table()

if __name__ == '__main__':
    # pobrać pass dla root
    print(f'\033[92m start server at {HOST} / {PORT} (Ctrl-C to stop application)')

server_socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(10)

while True:
    client_socket, address = server_socket.accept()
    data_from = client_socket.recv(8000)

    if data_from:
        try:
            data_pack = Crypt.decrypt(data_from)
            print(f'-------------------')
            print(f'otrzymana paczka -> {type(data_from)}--dł({len(data_from)})--{data_from}')
            print(f'rozkodowana paczka -> {type(data_pack)}--dł({len(data_pack)})--{data_pack}')

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

        # print(f"Uzyskano połączenie od hosta {address[0]} na porcie: {address[1]} wiadomość: {data_pack}")

        if msg_id == "user_check":
            # print(jobs.check_user(a_user, data3))
            # print(data3)
            msg_to_send = jobs.check_user(a_user, data3)

        elif msg_id == "get_user_list":
            msg_to_send = jobs.users_list()

        elif msg_id == "error":
            msg_to_send = "error"

        elif msg_id == "add_user":
            jobs.add_user(a_user, data2)
            msg_to_send = jobs.users_list()

        elif msg_id == "delete_user":
            jobs.delete_user(a_user)
            msg_to_send = jobs.users_list()

        elif msg_id == "host_memory":
            host = jobs.control_vm(f'free -m| grep Pam')
            # print(host)
            msg_to_send = host

        elif msg_id == "v_list":
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            msg_to_send = v_list

        elif msg_id == "get_logs":
            logs = jobs.read_logs_file()
            msg_to_send = logs

        elif msg_id == "reset_logs":
            logs = jobs.reset_logs(a_user)
            msg_to_send = logs

        elif msg_id == "get_vm_details":
            vm_details = jobs.make_vm_details(data2)
            msg_to_send = vm_details

        elif msg_id == "new_memory":
            # print(data2, data3)
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh setmem {data2} {data3}M')
            jobs.add_logs_entry(a_user, action=f'set memory {data2}: {data3} MB')
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            msg_to_send = v_list

        elif msg_id == "new_max_memory":
            # print(data2, data3)
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh setmaxmem {data2} {data3}M')
            jobs.add_logs_entry(a_user, action=f'set max memory {data2}: {data3} MB')
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            msg_to_send = v_list

        elif msg_id == "start":
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh start {data2} ')
            jobs.add_logs_entry(a_user, action=f'start {data2}')
            s = '--- komenda start dla '
            # print(msg_id, data2, s, data2)
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            msg_to_send = v_list

        elif msg_id == "stop":
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh shutdown {data2} ')
            jobs.add_logs_entry(a_user, action=f'stop {data2}')
            s = '--- komenda shutdown dla '
            # print(msg_id, data2, s, data2)
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            msg_to_send = v_list

        elif msg_id == "restart":
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh reboot {data2} ')
            jobs.add_logs_entry(a_user, action=f'reboot {data2}')
            s = '--- komenda reboot dla'
            # print(msg_id, data2, s, data2)
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            msg_to_send = v_list

        elif msg_id == "kill":
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh destroy {data2} ')
            jobs.add_logs_entry(a_user, action=f'force stop {data2}')
            s = '--- komenda destroy dla'
            # print(msg_id, data2, s, data2)

            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            msg_to_send = v_list

        else:
            msg_to_send = ['password_wrong']

        pack_to_send = Crypt.encrypt(msg_to_send)
        client_socket.send(pack_to_send)
        print(f'-------------------')
        print(f'przygotowana paczka -> {type(msg_to_send)}--dł({len(msg_to_send)})--{msg_to_send}')
        print(f'zakodowana paczka -> {type(pack_to_send)}--dł({len(pack_to_send)})--{pack_to_send}')

    else:
        print("<<< otrzymano pusty pakiet >>>")





