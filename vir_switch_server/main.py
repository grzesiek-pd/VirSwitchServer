import pickle
import socket as sock
import jobs
from time import sleep

HOST = '192.168.0.64'
PORT = 3333
jobs.create_table()

if __name__ == '__main__':
    print("--- start server ---")

server_socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(3)

while True:
    client_socket, address = server_socket.accept()
    data_from = client_socket.recv(32767)

    if data_from:
        print("otrzymany pakiet binarny: ", data_from)
        data_pack = pickle.loads(data_from)
        print(data_pack, type(data_pack))
        msg_id = data_pack[0]
        a_user = data_pack[1]
        data2 = data_pack[2]
        data3 = data_pack[3]

        print(f"Uzyskano połączenie od hosta {address[0]} na porcie: {address[1]} wiadomość: {data_pack}")

        if msg_id == "user_check":
            print(jobs.check_user(a_user, data3))
            print(data3)
            pack_msg = pickle.dumps(jobs.check_user(a_user, data3))

        elif msg_id == "get_user_list":
            pack_msg = pickle.dumps(jobs.users_list())

        elif msg_id == "add_user":
            jobs.add_user(a_user, data2)
            pack_msg = pickle.dumps(jobs.users_list())

        elif msg_id == "delete_user":
            jobs.delete_user(a_user)
            pack_msg = pickle.dumps(jobs.users_list())

        elif msg_id == "host_memory":
            host = jobs.control_vm(f'free -m| grep Mem')
            print(host)
            pack_msg = pickle.dumps(host)

        elif msg_id == "v_list":
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            pack_msg = pickle.dumps(v_list)

        elif msg_id == "get_logs":
            logs = jobs.read_logs_file()
            pack_msg = pickle.dumps(logs)

        elif msg_id == "reset_logs":
            logs = jobs.reset_logs(a_user)
            pack_msg = pickle.dumps(logs)

        elif msg_id == "new_memory":
            print(data2, data3)
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh setmem {data2} {data3}M')
            jobs.add_logs_entry(a_user, action=f'set memory {data2}: {data3} MB')
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            pack_msg = pickle.dumps(v_list)

        elif msg_id == "new_max_memory":
            print(data2, data3)
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh setmaxmem {data2} {data3}M')
            jobs.add_logs_entry(a_user, action=f'set maxmemory {data2}: {data3} MB')
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            pack_msg = pickle.dumps(v_list)

        elif msg_id == "start":
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh start {data2} ')
            jobs.add_logs_entry(a_user, action=f'start {data2}')
            s = '--- komenda start dla '
            print(msg_id, data2, s, data2)
            sleep(1)
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            pack_msg = pickle.dumps(v_list)

        elif msg_id == "stop":
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh shutdown {data2} ')
            jobs.add_logs_entry(a_user, action=f'stop {data2}')
            s = '--- komenda shutdown dla '
            print(msg_id, data2, s, data2)
            sleep(1)
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            pack_msg = pickle.dumps(v_list)

        elif msg_id == "restart":
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh reboot {data2} ')
            jobs.add_logs_entry(a_user, action=f'reboot {data2}')
            s = '--- komenda reboot dla'
            print(msg_id, data2, s, data2)
            sleep(1)
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            pack_msg = pickle.dumps(v_list)

        elif msg_id == "kill":
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh destroy {data2} ')
            jobs.add_logs_entry(a_user, action=f'force stop {data2}')
            s = '--- komenda destroy dla'
            print(msg_id, data2, s, data2)

            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            pack_msg = pickle.dumps(v_list)

        else:
            pack_msg = pickle.dumps(['password_wrong'])
        client_socket.send(pack_msg)
    else:
        print("<<< otrzymano pusty pakiet >>>")





