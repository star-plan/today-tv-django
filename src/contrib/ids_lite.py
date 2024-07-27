import requests

api_base = f'https://sso.cloud.unicomst.com'
client_id = '9432c6ce-f6b7-40a6-9d9c-5606cd06da26'
secret = 'd48c31eae70e49558220983f5d86e7a3'


def get_access_token():
    url = f'{api_base}/api/auth/access-token'
    resp = requests.post(url, json={
        'clientId': client_id,
        'securityKey': secret
    })

    data = resp.json()['data']

    return data['token']


def get_authorize_url(redirect_uri, response_type='code', scope='user-info', state=''):
    return (f'{api_base}/connect/authorize?'
            f'client_id={client_id}&'
            f'scope={scope}&'
            f'redirect_uri={redirect_uri}&'
            f'response_type={response_type}&'
            f'state={state}')


def get_user_info(code: str):
    token = get_access_token()
    url = f'{api_base}/api/auth/user-info/'
    resp = requests.get(url, params={
        'access_token': token,
        'code': code
    })

    data = resp.json()
    if data['successful']:
        return data['data']
    else:
        raise Exception(data['message'])


if __name__ == '__main__':
    get_user_info('cfd2b2cae8284785980ea79dc4a2f1da')
