#!/usr/bin  python3

import subprocess
import sys
import optparse


def check_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-i", "--interface", dest="interface",
                      help="Interface to change its MAC address.")

    (options, arguments) = parser.parse_args()
    return options


def replace_mac(options):
    if not options.interface:
        machine_data = str(subprocess.check_output(
            r"ifconfig | sed 's/^\(.*\): /\1---\n/g' | sed 's/\s*\(ether.*\)/\1---/g' | sed -n '/.*---/p' | sed 's/---// g'", shell=True)).replace(r"b'", '').replace("'", '').split(r'\n')[:-1]

        start = 1
        relevant_interfaces = {}

        while start < len(machine_data):
            if 'ether' in machine_data[start]:
                relevant_interfaces[start] = machine_data[start - 1]
            start += 1

        print(
            f"\nThose are available interfaces:{relevant_interfaces}\nPlease choose the interface by index.Insert the number:")

        try:
            interface = relevant_interfaces[int(input())]
        except KeyError:
            print('Interface does not exist!!')
            return
    else:
        interface = options.interface

    subprocess.call(['ifconfig', interface, 'down'])
    subprocess.call(f"service network-manager stop", shell=True)
    subprocess.call(['macchanger', '-r', interface])
    subprocess.call(f"service network-manager start", shell=True)
    subprocess.call(f"rfkill unblock all", shell=True)
    subprocess.call(['ifconfig', interface, 'up'])


if __name__ == '__main__':
    replace_mac(check_arguments())
