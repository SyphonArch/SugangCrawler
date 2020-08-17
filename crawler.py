import requests
from pprint import pprint
import re

records_per_page = 10
bait_regex = r'\d+ \(\d+\)'  # 정원 (재학생)
record_start = '<tr'
record_end = '</tr>'
search_result_count_regex = r'검색건수\s*<span.*>(\d+)</span>\s*건'

fields = ['교과구분', '개설대학', '개설학과', '이수과정', '학년', '교과목번호', '강좌번호', '교과목명',
          '학점-강의-실습', '수업교시', '수업형태', '강의실', '주담당교수', '강의계획서', '정원(재학생)',
          '수강신청인원', '비고']

url = 'http://sugang.snu.ac.kr/sugang/cc/cc100.action'


def search(subject_id, page_no):
    """Crawls the relevant page by subject_id and page_no, and returns the html text."""
    search_info = {'srchSbjtCd': subject_id, 'workType': 'S', 'pageNo': page_no}
    with requests.Session() as session:
        req = session.post(url, search_info)
    return req.text


def multipage_search(subject_id):
    """Crawls all pages of the search result of subject_id.
    Returns the html pages joined with a newline character."""
    page_no_to_check = 1
    pages = [search(subject_id, page_no_to_check)]
    target_page_no = find_max_page(pages[0])
    for page_no_to_check in range(2, target_page_no + 1):
        pages.append(search(subject_id, page_no_to_check))
    return '\n'.join(pages)


def course_no_search(subject_id, course_nos):
    """Crawl by subject_id and course_nos, which is a list of course numbers.
    Relevant pages will be crawled automatically.
    Returns the html pages joined with a newline character."""
    page_no_set = set()
    for course_no in course_nos:
        page_no_set.add((course_no + records_per_page - 1) // records_per_page)
    pages = []
    for page_no in page_no_set:
        pages.append(search(subject_id, page_no))
    return '\n'.join(pages)


def find_max_page(html_text):
    """Given a single page, will find the search result count,
    and calculate the number of pages required to show all search results."""
    pattern = re.compile(search_result_count_regex)
    pattern_matches = pattern.findall(html_text)
    assert len(pattern_matches) == 1
    record_count = int(pattern_matches[0])
    return (record_count + records_per_page - 1) // records_per_page


def bidirectional_search(text, start_pos):
    """From the given position in text, will look for the opening and closing tags specified by
    record_start and record_end. Returns the indexes of the start and end of found record.
    Returned index is inclusive for front, and non-inclusive for back."""
    front = start_pos
    back = start_pos
    while text[front:front + len(record_start)] != record_start:
        front -= 1
    while text[back:back + len(record_end)] != record_end:
        back += 1
    back += len(record_end)
    return front, back


def extract_records(html_text):
    """Extracts the relevant text sections containing records from the whole html text."""
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
    """Strips tags from text."""
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
    """Given the html text for a record, parses the text to package the data into a dictionary."""
    lines = [line.strip() for line in record_text.split('\n')]
    lines = lines[2:-1]  # <tr>와 </tr>, checkbox 제거
    lines = [tag_strip(line) for line in lines]
    assert len(lines) == len(fields)
    record_data = {}
    for field_name, data in zip(fields, lines):
        record_data[field_name] = data
    return record_data


def course_no_to_records(subject_id, course_nos):
    """Crawls the relevant pages, then filters the relevant records by subject_id and course_nos.
    course_nos is a list of course numbers.
    Returns records as a list of dictionaries."""
    html_text = course_no_search(subject_id, course_nos)
    all_record_texts = extract_records(html_text)
    all_records = [parse_record(record_text) for record_text in all_record_texts]

    filtered_records = [record for record in all_records if int(record['강좌번호']) in course_nos]
    return filtered_records


if __name__ == '__main__':
    from time import time
    st = time()
    
    target_subject_id = 'L0440.000600'
    target_course_nos = [3, 13, 23]
    records = course_no_to_records(target_subject_id, target_course_nos)

    #for record in records:
        #pprint(record)
        #print('\n\n')

    #print(f"{len(records)} records found.")

    print(time() - st)
