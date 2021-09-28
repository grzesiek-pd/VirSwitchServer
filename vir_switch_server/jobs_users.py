import jobs_logs
import sqlite3
import hashlib

c = sqlite3.connect('users.db')
cursor = c.cursor()


def create_table():
    init_pass = hashlib.md5(b'admin').hexdigest()
    query = f"CREATE TABLE IF NOT EXISTS users(login TEXT , password TEXT , admin TEXT , vms TEXT );"
    cursor.execute(query)
    query2 = f"SELECT login FROM users WHERE admin = 'yes';"
    cursor.execute(query2)
    admins = cursor.fetchall()
    c.commit()
    if len(admins) == 0:
        print(f'no admins (creating user:admin/pass:admin - Please create another admin account and remove this!)')
        query2 = f"INSERT INTO users(login, password, admin, vms) VALUES ('admin','{init_pass}', 'yes', 'all');"
        cursor.execute(query2)
        c.commit()


def add_user(username, user_data):
    pass_hash = user_data[0]
    is_admin = user_data[1]
    vms = user_data[2]

    query = "INSERT INTO users(login, password, admin, vms) VALUES (?, ?, ?, ?);"
    cursor.execute(query, (username, pass_hash, is_admin, vms))
    print(f'add user: {username}')
    c.commit()


def delete_user(username):
    query = f"DELETE FROM users WHERE login ='{username}';"
    cursor.execute(query)
    print(f'delete user: {username}')
    c.commit()


def update_user_vm_list(username, vm, action):
    query = f"SELECT vms FROM users WHERE login = '{username}';"
    cursor.execute(query)
    vms_tuple = cursor.fetchone()
    c.commit()
    vm_list = []
    try:
        vm_list = list(vms_tuple)[0].split(",")
    except TypeError as err:
        print(err)
    if action == 'remove':
        try:
            vm_list.remove(vm)
            print(f'remove user: {username} from vm: {vm}')
        except ValueError as err:
            print(err)
    elif action == 'add':
        vm_list.append(vm)
        print(f'add user: {username} to vm: {vm}')

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
            jobs_logs.add_logs_entry(user, action=f'login to server')
            print(f'log in user: {user}')
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

