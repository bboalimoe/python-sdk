# coding: utf-8

import json

import requests

import leancloud

__author__ = 'asaka <lan@leancloud.rocks>'


APP_ID = None
APP_KEY = None
MASTER_KEY = None

CN_BASE_URL = 'https://cn.avoscloud.com'
US_BASE_URL = 'https://us.avoscloud.com'

SERVER_VERSION = '1.1'
SDK_VERSION = '0.0.1'
BASE_URL = CN_BASE_URL + '/' + SERVER_VERSION

headers = None


def init(app_id, app_key=None, master_key=None):
    if (not app_key) and (not master_key):
        raise RuntimeError('app_key or master_key must be specified')
    if app_key and master_key:
        raise RuntimeError('app_key and master_key can\'t be specified both')

    global APP_ID, APP_KEY, MASTER_KEY
    APP_ID = app_id
    APP_KEY = app_key
    MASTER_KEY = master_key


def need_init(func):
    def new_func(*args, **kwargs):
        if APP_ID is None:
            raise RuntimeError('LeanCloud SDK must be initialized')

        global headers
        if not headers:
            headers = {}
        headers['X-AVOSCloud-Application-Id'] = APP_ID
        headers['User-Agent'] = 'AVOS Cloud python-{} SDK'.format(leancloud.__version__)
        if APP_KEY:
            headers['X-AVOSCloud-Application-Key'] = APP_KEY
        else:
            headers['X-AVOSCloud-Master-Key'] = MASTER_KEY

        return func(*args, **kwargs)
    return new_func


def check_error(func):
    def new_func(*args, **kwargs):
        response = func(*args, **kwargs)
        assert isinstance(response, requests.Response)
        if response.headers['Content-Type'] == 'text/html':
            raise leancloud.LeanCloudError(-1, 'Bad Request')
        content = response.json()
        if 'error' in content:
            raise leancloud.LeanCloudError(content['code'], content['error'])
        return response
    return new_func


@need_init
@check_error
def get(url, params):
    for k, v in params.iteritems():
        if isinstance(v, dict):
            params[k] = json.dumps(v)
    response = requests.get(BASE_URL + url, headers=headers, params=params)
    return response


@need_init
@check_error
def post(url, params):
    response = requests.post(BASE_URL + url, headers=headers, json=params)
    return response


@need_init
@check_error
def put(url, params):
    response = requests.post(BASE_URL + url, headers=headers, json=params)
    return response


@need_init
@check_error
def delete(url, params=None):
    response = requests.delete(BASE_URL + url, headers=headers, json=params)
    return response
