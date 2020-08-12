import requests
import re

master_regex = r'<.*>\s*(?P<정원>\d+)\s*\((?P<재학생>\d+)\)\s*<.*>\s*' \
               r'<.*>\s*(?P<수강신청인원>\d+)\s*<.*>'
url = 'http://sugang.snu.ac.kr/sugang/cc/cc100.action'


def search(subject_id):
    search_info = {'srchSbjtCd': subject_id, 'workType': 'S'}
    with requests.Session() as session:
        req = session.post(url, search_info)
    return req.text


def get_applicant_counts(html):
    pattern = re.compile(master_regex)
    matches = pattern.findall(html)
    return matches


if __name__ == '__main__':
    html = search('033.019')  # 통계학
    print(get_applicant_counts(html))
