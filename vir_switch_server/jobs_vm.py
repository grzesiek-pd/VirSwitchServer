import subprocess
from subprocess import PIPE


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
        v_list_info.append(li[1])

    for vm in v_list_info:
        try:
            p = subprocess.Popen(f'virsh dominfo {vm} | grep "\(State\|memory\|CPU\)"', stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True)
            stdout, stderr = p.communicate()

            out = stdout.decode('utf-8')
            err = stderr.decode('utf-8')
            info = []
        except Exception as er:
            er = str(err)
            print(er)

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
            p = subprocess.Popen(f'virsh desc {vm}', stdout=PIPE, stderr=PIPE, stdin=PIPE, shell=True)
            stdout, stderr = p.communicate()

            vm_description_str = stdout.decode('utf-8')
            err2 = stderr.decode('utf-8')

            if vm_description_str.startswith('No'):
                description_ip = "No description!"
                description_pwd = "No description!"
            else:
                desc_dict = eval(vm_description_str)
                description_ip = desc_dict["ip"]
                description_pwd = desc_dict["root_pwd"]
        except Exception as er:
            err2 = str(er)
        info.append(description_ip)
        info.append(description_pwd)
        v_list.append(info)
    return v_list


def update_description(data2, data3):
    vm = data2
    vm_ip = data3.get('ip')
    vm_pass = data3.get('pass')
    try:
        p = subprocess.Popen(f'virsh desc {vm} --new-desc ' +
                             "'{" + f'"ip": "{vm_ip}", "root_pwd": "{vm_pass}"'+"}'", stdout=PIPE, stderr=PIPE, stdin=PIPE,
                             shell=True)
        stdout, stderr = p.communicate()
        print(f'update description for vm: {data2} ({data3})')

        vm_description_str = stdout.decode('utf-8')
        err = stderr.decode('utf-8')

    except Exception as er:
        err = str(er)
        print(vm_description_str)
        print(err)
        print(er)
    return None


