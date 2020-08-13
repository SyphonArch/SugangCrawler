import requests
from pprint import pprint
import re

bait_regex = r'\d+ \(\d+\)'  # 정원 (재학생)
record_start = '<tr'
record_end = '</tr>'
page_number_regex = r'<a href="javascript:fnGotoPage\((\d+)\);"'

fields = ['교과구분', '개설대학', '개설학과', '이수과정', '학년', '교과목번호', '강좌번호', '교과목명',
          '학점-강의-실습', '수업교시', '수업형태', '강의실', '주담당교수', '강의계획서', '정원(재학생)',
          '수강신청인원', '비고']

url = 'http://sugang.snu.ac.kr/sugang/cc/cc100.action'


def search(subject_id, page_no):
    search_info = {'srchSbjtCd': subject_id, 'workType': 'S', 'pageNO': page_no}
    with requests.Session() as session:
        req = session.post(url, search_info)
    return req.text


def auto_search(subject_id):
    pages = []
    page_no_to_check = 1
    target_page_no = 1
    while True:
        while page_no_to_check <= target_page_no:
            pages.append(search(subject_id, page_no_to_check))
            page_no_to_check += 1
        max_page_no = find_max_page(pages[-1])
        if max_page_no > target_page_no:
            target_page_no = max_page_no
        else:
            break
    return '\n'.join(pages)


def find_max_page(html_text):
    pattern = re.compile(page_number_regex)
    page_numbers = list(map(int, pattern.findall(html_text)))
    if len(page_numbers) == 0:
        return 1  # 페이지가 하나인 경우, 다음 페이지로 가는 링크가 없다
    else:
        return max(page_numbers)


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
    html = auto_search('033.020')  # 통계학실험
    record_texts = get_records(html)
    records = [parse_record(record_text) for record_text in record_texts]
    for record in records:
        pprint(record)
        print('\n\n')

    print(f"{len(records)} records found.")
