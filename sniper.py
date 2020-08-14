from time import sleep
from crawler import course_no_to_records
import emailer
from configurations import target_courses


def course_identifier(subject_id, course_no):
    return subject_id, course_no


initial_registrant_counts = {}

while True:
    for subject_id in target_courses:
        print(f"{subject_id} 확인중")
        # 모든 강좌번호에 대해 검색해서 결과 저장하기
        course_nos = target_courses[subject_id]
        records = course_no_to_records(subject_id, course_nos)

        for record in records:
            course_id = course_identifier(subject_id, record['강좌번호'])
            registrant_count = int(record['수강신청인원'])
            # 첫 검색인 경우, 수강신청인원을 기록한다.
            if course_id not in initial_registrant_counts:
                initial_registrant_counts[course_id] = registrant_count
            else:
                if registrant_count < initial_registrant_counts[course_id]:
                    emailer.send(f"{subject_id} 빈자리 알림",
                                 f"{subject_id}의 {record['강좌번호']} 분반에 자리가 확인되었습니다.\n\n"
                                 f"sugang.snu.ac.kr")
                    print('Message Sent!')
                    initial_registrant_counts[course_id] = registrant_count
    print(initial_registrant_counts)
    sleep(5)  # delay between checks
