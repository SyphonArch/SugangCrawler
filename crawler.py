import requests
from pprint import pprint
import re

bait_regex = r'\d+ \(\d+\)'  # 정원 (재학생)
record_start = '<tr'
record_end = '</tr>'
fields = ['교과구분', '개설대학', '개설학과', '이수과정', '학년', '교과목번호', '강좌번호', '교과목명',
          '학점-강의-실습', '수업교시', '수업형태', '강의실', '주담당교수', '강의계획서', '정원(재학생)',
          '수강신청인원', '비고']
url = 'http://sugang.snu.ac.kr/sugang/cc/cc100.action'


def search(subject_id):
    search_info = {'srchSbjtCd': subject_id, 'workType': 'S'}
    with requests.Session() as session:
        req = session.post(url, search_info)
    return req.text


def bidirectional_search(text, start_pos):
    front = start_pos
    back = start_pos
    while text[front:front + len(record_start)] != record_start:
        front -= 1
    while text[back:back + len(record_end)] != record_end:
        back += 1
    back += len(record_end)
    return front, back


def get_records(html_text):
    pattern = re.compile(bait_regex)
    bait_indexes = [m.start() for m in re.finditer(pattern, html_text)]

    record_ranges = []
    for bait_index in bait_indexes:
        record_ranges.append(bidirectional_search(html_text, bait_index))

    record_texts = []
    for record_range in record_ranges:
        record_texts.append(html_text[record_range[0]:record_range[1]])

    return record_texts


def tag_strip(text):
    buffer = []
    opened_tag_count = 0
    for char in text:
        if char == '<':
            opened_tag_count += 1
        elif char == '>':
            opened_tag_count -= 1
        else:
            if opened_tag_count == 0:
                buffer.append(char)
    return ''.join(buffer)


def parse_record(record_text):
    lines = [line.strip() for line in record_text.split('\n')]
    lines = lines[2:-1]  # <tr>와 </tr>, checkbox 제거
    lines = [tag_strip(line) for line in lines]
    assert len(lines) == len(fields)
    record_data = {}
    for field_name, data in zip(fields, lines):
        record_data[field_name] = data
    return record_data


if __name__ == '__main__':
    html = search('033.019')  # 통계학
    record_texts = get_records(html)
    records = [parse_record(record_text) for record_text in record_texts]
    for record in records:
        pprint(record)
        print('\n\n')
