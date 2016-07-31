import requests
import httplib2
from time import time

def captcha_save(url):
    img = requests.get(url)
    out = open(r'captcha/{}.jpg'.format(int(time() * 100)), 'wb')
    out.write(img.content)
    out.close()

def captcha_save2(url):
    h = httplib2.Http('.cache')
    response, content = h.request(url)
    out = open(r'captcha/{}.jpg'.format(int(time() * 100)), 'wb')
    out.write(content)
    out.close()

