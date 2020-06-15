#!/root/anaconda3/bin  python
import requests
import os
import re
import urllib

curren_dir = os.path.dirname(os.path.abspath(__file__))


def request(url):
    try:
        return requests.get(f'http://{url}')
    except requests.exceptions.ConnectionError:
        pass
    except NameError as err:
        print(f'NameError: {err}')
    except requests.exceptions.InvalidURL as err:
        print(f'Invalid URL: {err}')
    except UnicodeError as err:
        print(f'UnicodeError: {err}')


def extract_links_from(url):
    responce = request(url)
    return re.findall('(?:href=")(.*?)"', responce.content.decode()) if responce else None


# target_url = 'zsecurity.org'
target_url = '192.168.1.127/mutillidae/'
target_links = set()


def crawl(target_url):
    links = extract_links_from(target_url)
    if links is not None:
        for link in links:
            link = urllib.parse.urlparse(target_url, link)
            if not 'http' in link.scheme:
                link = f'http://{link.path}{link.scheme}'
            else:
                link = link.scheme
            if target_url in link:
                if '#' in link:
                    link = link.split('#')[0]
                if link not in target_links:
                    target_links.add(link)
                    crawl(link)


if __name__ == '__main__':
    crawl(target_url)
    for el in target_links:
        print(el)
