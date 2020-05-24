#!/usr/bin  python3

import scapy.all as scapy
import subprocess


def scan(ip):
    scapy.arping(ip)


gateway = str(subprocess.check_output(
    r"route -n | awk 'FNR == 3 {print $2;exit}'", shell=True)).replace(r"b'", '').replace("\\n'", '')

scan(f"{gateway}/24")
