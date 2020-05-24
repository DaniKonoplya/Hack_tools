#!/usr/bin  python3

import scapy.all as scapy
import subprocess
import optparse


def check_arguments():
    parser = optparse.OptionParser()
    parser.add_option("--t", "--target", dest="target",
                      help="Set target machines range. Example 10.0.2.1/24")

    (options, arguments) = parser.parse_args()
    return options


def scan(ip):
    arp_request = scapy.ARP(pdst=ip)
    broadcast = scapy.Ether(dst="ff:ff:ff:ff:ff:ff")
    arp_request_broadcast = broadcast/arp_request
    answered_list, _ = scapy.srp(arp_request_broadcast, timeout=1)

    clients_list = []
    for element in answered_list:
        clients_dict = {"ip": element[1].psrc, "mac": element[1].hwsrc}
        clients_list.append(clients_dict)
    return clients_list


def print_results(results_list):
    print(f"IP\t\t\tMAC Adress\n{'-' * 100}\n")
    for client in results_list:
        print(client['ip'], end='\t\t')
        print(client['mac'])


if __name__ == '__main__':
    options = check_arguments()

    if not options.target:
        gateway = str(subprocess.check_output(
            r"route -n | awk 'FNR == 3 {print $2;exit}'", shell=True)).replace(r"b'", '').replace("\\n'", '') + r'/24'
    else:
        gateway = options.target

    print_results(scan(gateway))
