import requests
import urllib.request
from bs4 import BeautifulSoup as bs
import time
import re


course_total_td_num = 21
applied_num_index = 16
appliable_num_index = 15

regex = r'<.*>\s*(\d+)\s*\((\d+)\)\s*<.*>\s*<.*>\s*(\d+)\s*<.*>'


def split_course(td_list):
    return [td_list[c: c + course_total_td_num] for c in range(0, len(td_list), course_total_td_num)]


def get_applied_num(course):
    return int(course[applied_num_index].get_text())


def get_appliable_num(course):
    return int(course[appliable_num_index].get_text().split(' ')[0])


def search(subject_id):
    search_info = {'srchSbjtCd': subject_id, 'workType': 'S'}
    with requests.Session() as s:
        print()
        req = s.post('http://sugang.snu.ac.kr/sugang/cc/cc100.action', search_info)
        soup = bs(req.text, 'lxml')
        table = soup.find('table', {'class': 'tbl_basic'})
        table_td = table.findChildren('td')
        course_list = split_course(table_td)
        for course in course_list:
            print(f"{get_applied_num(course)} / {get_appliable_num(course)}")


def search2(subject_id):
    search_info = {'srchSbjtCd': subject_id, 'workType': 'S'}
    with requests.Session() as s:
        print()
        req = s.post('http://sugang.snu.ac.kr/sugang/cc/cc100.action', search_info)
        html = req.text
        pattern = re.compile(regex)
        matches = pattern.findall(html)
        print(matches)


