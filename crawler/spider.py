#!/root/anaconda3/bin  python

"""
python /root/Documents/Python/Hacking/Hack_tools/crawler/spider.py | sed 's/.*\(You have logged[^/]*\)<.*/\1/g'

"""
import requests

target_url = 'http://192.168.1.127/dvwa/login.php'

data_dict = {'username': 'admin', 'password': 'password', 'Login': 'submit'}

responce = requests.post(target_url, data=data_dict)
print(responce.content)
