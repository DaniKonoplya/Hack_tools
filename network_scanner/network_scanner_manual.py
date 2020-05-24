#!/usr/bin  python3

import scapy.all as scapy
import subprocess


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


gateway = str(subprocess.check_output(
    r"route -n | awk 'FNR == 3 {print $2;exit}'", shell=True)).replace(r"b'", '').replace("\\n'", '')

print_results(scan(f"{gateway}/24"))
