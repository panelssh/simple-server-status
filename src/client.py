#!/usr/bin/env python3

import collections
import subprocess
import json
import os
import re
import time
import socket

SERVER_HOST = "localhost"
SERVER_PORT = 35600
HOSTNAME = "localhost"


def get_uptime():
    f_open = open('/proc/uptime', 'r')
    n_uptime = f_open.readline()
    f_open.close()
    return int(n_uptime.split('.', 2)[0])


def get_memory():
    re_parser = re.compile(r'^(?P<key>\S*):\s*(?P<value>\d*)\s*kB')
    result = dict()
    for line in open('/proc/meminfo'):
        match = re_parser.match(line)
        if not match:
            continue
        # noinspection PyTypeChecker
        key, value = match.groups(['key', 'value'])
        result[key] = int(value)

    MemTotal = float(result['MemTotal'])
    MemFree = float(result['MemFree'])
    Cached = float(result['Cached'])
    MemUsed = MemTotal - (Cached + MemFree)
    n_swap_total = float(result['SwapTotal'])
    n_swap_free = float(result['SwapFree'])
    return int(MemTotal), int(MemUsed), int(n_swap_total), int(n_swap_free)


def get_hdd():
    p = subprocess.check_output([
        'df',
        '-Tlm',
        '--total',
        '-t',
        'ext4',
        '-t',
        'ext3',
        '-t',
        'ext2',
        '-t',
        'reiserfs',
        '-t',
        'jfs',
        '-t',
        'ntfs',
        '-t',
        'fat32',
        '-t',
        'btrfs',
        '-t',
        'fuseblk',
        '-t',
        'zfs',
        '-t',
        'simfs',
        '-t',
        'xfs'
    ]).decode("Utf-8")
    total = p.splitlines()[-1]
    used = total.split()[3]
    size = total.split()[2]
    return int(size), int(used)


def get_load():
    return os.getloadavg()[0]


def get_time():
    stat_file = open('/proc/stat', 'r')
    time_list = stat_file.readline().split(' ')[2:6]
    stat_file.close()
    for i in range(len(time_list)):
        # noinspection PyTypeChecker
        time_list[i] = int(time_list[i])
    return time_list


def delta_time():
    x = get_time()
    time.sleep(5)
    y = get_time()
    for i in range(len(x)):
        y[i] -= x[i]
    return y


def get_cpu():
    t = delta_time()
    st = sum(t)
    if st == 0:
        st = 1
    # noinspection PyTypeChecker
    result = 100 - (t[len(t) - 1] * 100.00 / st)
    return round(result)


def get_service(ps_name):
    ps = subprocess.Popen("ps axf | grep %s | grep -v grep | wc -l" % ps_name, shell=True, stdout=subprocess.PIPE)
    output = ps.stdout.read()
    ps.stdout.close()
    ps.wait()
    return int(output) > 0


def get_user(c, f):
    subprocess.call(c, shell=True)
    with open(f, 'r') as d:
        output = d.read()
        return json.loads(output)


class Traffic:
    def __init__(self):
        self.rx = collections.deque(maxlen=10)
        self.tx = collections.deque(maxlen=10)

    def get(self):
        f = open('/proc/net/dev', 'r')
        net_dev = f.readlines()
        f.close()
        avg_rx = 0
        avg_tx = 0

        for dev in net_dev[2:]:
            dev = dev.split(':')
            if dev[0].strip() == "lo" or dev[0].find("tun") > -1:
                continue
            dev = dev[1].split()
            avg_rx += int(dev[0])
            avg_tx += int(dev[8])

        self.rx.append(avg_rx)
        self.tx.append(avg_tx)
        avg_rx = 0
        avg_tx = 0

        rx = len(self.rx)
        for x in range(rx - 1):
            avg_rx += self.rx[x + 1] - self.rx[x]
            avg_tx += self.tx[x + 1] - self.tx[x]

        return int(avg_rx / rx / 1), int(avg_tx / rx / 1)


def get_timezone():
    ps = subprocess.Popen("cat /etc/timezone", shell=True, stdout=subprocess.PIPE)
    timezone = ps.stdout.read()
    ps.stdout.close()
    ps.wait()
    return timezone.decode().rstrip()


if __name__ == '__main__':
    socket.setdefaulttimeout(30)

    while 1:
        try:
            # print("Connecting...")
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((SERVER_HOST, SERVER_PORT))

            # print("Get Traffic...")
            traffic = Traffic()

            while 1:
                # print("Get Uptime...")
                uptime = get_uptime()
                # print("Get Load...")
                load = get_load()
                # print("Get CPU...")
                cpu = get_cpu()
                # print("Get Network...")
                net_rx, net_tx = traffic.get()
                # print("Get Memory...")
                memory_total, memory_used, swap_total, swap_free = get_memory()
                # print("Get HDD...")
                hdd_total, hdd_used = get_hdd()

                # print("Get SSHD...")
                sshd = get_service('sshd')
                # print("Get Stunnel4...")
                stunnel4 = get_service('stunnel4')
                # print("Get OpenVPN...")
                openvpn = get_service('openvpn')
                # print("Get Dropbear...")
                dropbear = get_service('dropbear')
                # print("Get Squid...")
                squid = get_service('squid')
                # print("Get Squid3...")
                squid3 = get_service('squid3')
                # print("Get BadVPN...")
                badvpn = get_service('badvpn-udpgw')
                # print("Get L2tp...")
                l2tp = get_service('xl2tpd')
                # print("Get IPsec...")
                ipsec = get_service('ipsec')
                # print("Get Wireguard...")
                wireguard = get_service('wg')
                # print("Get Trojan...")
                trojan = get_service('trojan')
                # print("Get Shadowsocks...")
                shadowsocks = get_service('shadowsocks')
                # print("Get Nginx...")
                nginx = get_service('nginx')

                array = {
                    'hostname': HOSTNAME,
                    'uptime': uptime,
                    'cpu': cpu,
                    'load': load,
                    'memory': {
                        'total': memory_total,
                        'used': memory_used
                    },
                    'swap': {
                        'total': swap_total,
                        'used': swap_total - swap_free
                    },
                    'hdd': {
                        'total': hdd_total,
                        'used': hdd_used
                    },
                    'network': {
                        'rx': net_rx,
                        'tx': net_tx
                    },
                    'services': {
                        'sshd': sshd,
                        'stunnel4': stunnel4,
                        'openvpn': openvpn,
                        'dropbear': dropbear,
                        'squid': squid,
                        'squid3': squid3,
                        'badvpn': badvpn,
                        'l2tp': l2tp,
                        'ipsec': ipsec,
                        'wireguard': wireguard,
                        'trojan': trojan,
                        'shadowsocks': shadowsocks,
                        'nginx': nginx
                    },
                    'updated_at': int(time.time()),
                    'timezone': get_timezone()
                }

                s.send(json.dumps(array).encode())

                time.sleep(5)
        except KeyboardInterrupt:
            raise
        except socket.error as e:
            print("Disconnected...", e)

            time.sleep(10)
        except Exception as e:
            print("Caught Exception:", e)

            time.sleep(10)
