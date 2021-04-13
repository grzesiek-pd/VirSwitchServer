import pickle
import socket as sock
import jobs
from time import sleep
from cryptography.fernet import Fernet

key = b'8tnFL71voDHkQ3V7XySswRC2ZHOIfB7lDt11n4OieQQ='
HOST = '192.168.81.131'
PORT = 3333
jobs.create_table()

if __name__ == '__main__':
    print(f'\033[92m start server at {HOST} / {PORT} (Ctrl-C to stop application)')

server_socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(5)

while True:
    client_socket, address = server_socket.accept()
    data_from = client_socket.recv(32767)

    if data_from:
        try:
            encoded_mag = Fernet(key).decrypt(data_from)
            data_pack = eval(encoded_mag.decode())

            # data_pack = pickle.loads(data_from)
            print("otrzymany pakiet binarny: ", data_from)
            print(data_pack, type(data_pack))
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
            _msg = jobs.check_user(a_user, data3)

        elif msg_id == "get_user_list":
            _msg = jobs.users_list()

        elif msg_id == "error":
            _msg = "error"

        elif msg_id == "add_user":
            jobs.add_user(a_user, data2)
            _msg = jobs.users_list()

        elif msg_id == "delete_user":
            jobs.delete_user(a_user)
            _msg = jobs.users_list()

        elif msg_id == "host_memory":
            host = jobs.control_vm(f'free -m| grep Pam')
            # print(host)
            _msg = host

        elif msg_id == "v_list":
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            _msg = v_list

        elif msg_id == "get_logs":
            logs = jobs.read_logs_file()
            _msg = logs

        elif msg_id == "reset_logs":
            logs = jobs.reset_logs(a_user)
            _msg = logs

        elif msg_id == "new_memory":
            # print(data2, data3)
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh setmem {data2} {data3}M')
            jobs.add_logs_entry(a_user, action=f'set memory {data2}: {data3} MB')
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            _msg = v_list

        elif msg_id == "new_max_memory":
            # print(data2, data3)
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh setmaxmem {data2} {data3}M')
            jobs.add_logs_entry(a_user, action=f'set max memory {data2}: {data3} MB')
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            _msg = v_list

        elif msg_id == "start":
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh start {data2} ')
            jobs.add_logs_entry(a_user, action=f'start {data2}')
            s = '--- komenda start dla '
            # print(msg_id, data2, s, data2)
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            _msg = v_list

        elif msg_id == "stop":
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh shutdown {data2} ')
            jobs.add_logs_entry(a_user, action=f'stop {data2}')
            s = '--- komenda shutdown dla '
            # print(msg_id, data2, s, data2)
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            _msg = v_list

        elif msg_id == "restart":
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh reboot {data2} ')
            jobs.add_logs_entry(a_user, action=f'reboot {data2}')
            s = '--- komenda reboot dla'
            # print(msg_id, data2, s, data2)
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            _msg = v_list

        elif msg_id == "kill":
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh destroy {data2} ')
            jobs.add_logs_entry(a_user, action=f'force stop {data2}')
            s = '--- komenda destroy dla'
            # print(msg_id, data2, s, data2)

            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            _msg = v_list

        else:
            _msg = ['password_wrong']

        a = str(_msg)
        b = pickle.dumps(a)

        c = pickle.loads(b)
        d = eval(c)

        print('-->', type(_msg), _msg)
        print('-->', type(a), a)
        print('-->', type(b), b)
        print('-->', type(c), c)
        print('-->', type(d), d)

        msg_str = str(_msg)

        if len(msg_str) > 1000:
            parts = int(len(msg_str) / 1000 + 1)
            _msg = pickle.dumps(parts)
            client_socket.send(_msg)

            for i in range(parts):
                part = msg_str[0 + i * 1000: 1000 + (i + 1) * 1000]
                part_encode = part.encode("utf-8")
                # part_encode = f' *** part {i} ***'.encode("utf-8")
                print(f'part {i}', len(part), part)
                print(f'part {i}', len(part_encode), part_encode)

                client_socket.send(part_encode)

        else:
            pack_msg = pickle.dumps(_msg)
            client_socket.send(pack_msg)
    else:
        print("<<< otrzymano pusty pakiet >>>")





