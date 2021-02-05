import pickle
import socket as sock
import jobs
from time import sleep

HOST = '192.168.0.64'
PORT = 4444

if __name__ == '__main__':
    print("--- start server ---")

server_socket = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
server_socket.bind((HOST, PORT))
server_socket.listen(3)


while True:
    client_socket, address = server_socket.accept()
    data_from = client_socket.recv(50000)

    users = jobs.read_users_file()

    if data_from:
        print("otrzymany pakiet binarny: ", data_from)
        log_and_pas = pickle.loads(data_from)
        print(log_and_pas, type(log_and_pas))
        msg_id = log_and_pas[0]
        data2 = log_and_pas[1]
        data3 = log_and_pas[2]

        print(f"Uzyskano połączenie od hosta {address[0]} na porcie: {address[1]} wiadomość: {log_and_pas}")

        if msg_id == "user_check":
            jobs.add_logs_entry(data2, address, action='login')
            if data2 in list(users.keys()) and data3 == users[data2][0]:
                pack_msg = pickle.dumps(['password_ok', data2, users[data2][0], users[data2][1], users[data2][2]])
            else:
                pack_msg = pickle.dumps(['password_wrong'])

        elif msg_id == "get_user_list":

            pack_msg = pickle.dumps(users)

        elif msg_id == "v_list":

            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            pack_msg = pickle.dumps(v_list)

        elif msg_id == "get_logs":
            logs = jobs.read_logs_file()
            print(type(logs), logs)
            pack_msg = pickle.dumps(logs)

        elif msg_id == "start":
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh start {data2} ')
            s = '--- komenda start dla '
            print(msg_id, data2, s, data2)
            sleep(1)
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            pack_msg = pickle.dumps(v_list)

        elif msg_id == "stop":
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh shutdown {data2} ')
            s = '--- komenda shutdown dla '
            print(msg_id, data2, s, data2)
            sleep(1)
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            pack_msg = pickle.dumps(v_list)

        elif msg_id == "restart":
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh reboot {data2} ')
            s = '--- komenda reboot dla'
            print(msg_id, data2, s, data2)
            sleep(1)
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            pack_msg = pickle.dumps(v_list)

        elif msg_id == "kill":
            jobs.control_vm(f'echo "gugugu" | sudo -S virsh destroy {data2} ')
            s = '--- komenda destroy dla'
            print(msg_id, data2, s, data2)
            sleep(1)
            v_list = jobs.make_vm_list('echo "gugugu" | sudo -S virsh list --all ')
            pack_msg = pickle.dumps(v_list)

        else:
            pack_msg = pickle.dumps(['password_wrong'])

        client_socket.send(pack_msg)

    else:
        print("<<< otrzymano pusty pakiet >>>")





