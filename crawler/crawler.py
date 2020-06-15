#!/root/anaconda3/bin  python

import requests
import os

curren_dir = os.path.dirname(os.path.abspath(__file__))


def request(url):
    try:
        return requests.get(f'http://{url}', verify=False, timeout=3)
    except requests.exceptions.ConnectionError:
        pass
    except NameError as err:
        print(f'NameError: {err}')
    except requests.exceptions.InvalidURL as err:
        print(f'Invalid URL: {err}')
    except UnicodeError as err:
        print(f'UnicodeError: {err}')


target_url = '192.168.1.127/mutillidae/'
counter = 0 

# with open(f'{curren_dir}/word_list.txt') as wordlist_file:
with open(f'{curren_dir}/common.txt') as wordlist_file:
    for line in wordlist_file:
        word = line.strip()
        # test_url = f'{word}.{target_url}'
        test_url = f'{target_url}/{word}'
        responce = request(test_url)
        if responce:
            print(f'[+] Discovered subdomain --> {test_url}')
        if counter > 4000:
            break
        counter += 1
