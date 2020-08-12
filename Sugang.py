import requests
from bs4 import BeautifulSoup as bs
import time
import re

regex = r'<.*>\s*(\d+)\s*\((\d+)\)\s*<.*>\s*<.*>\s*(\d+)\s*<.*>'


def search(subject_id):
    search_info = {'srchSbjtCd': subject_id, 'workType': 'S'}
    with requests.Session() as s:
        req = s.post('http://sugang.snu.ac.kr/sugang/cc/cc100.action', search_info)
        s = time.time()
        html = req.text
        pattern = re.compile(regex)
        matches = pattern.findall(html)
        print(time.time() - s)
        print(matches)
