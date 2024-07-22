from requests import Session

session = Session()


class ProxyPool(object):
    def __init__(self, api_base: str):
        self.api_base = api_base

    def get_list(self):
        resp = session.get(f'{self.api_base}/all').json()
        return [f'http://{p["proxy"]}' for p in resp]

    def get_one(self) -> str:
        resp = session.get(f'{self.api_base}/get').json()
        proxy_url = resp['proxy']
        return f'http://{proxy_url}'

    def delete(self, proxy: str):
        session.get(f"{self.api_base}/delete/?proxy={proxy}")


if __name__ == '__main__':
    p = ProxyPool()
    print(p.get_one())
    # print(p.get_list())
