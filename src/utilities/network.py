from pprint import pprint
from requests import Session

session = Session()


def whats_my_ip():
    resp = session.get('http://ip-api.com/json/')
    return resp.json()


if __name__ == '__main__':
    pprint(whats_my_ip())
