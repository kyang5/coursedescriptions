#!/usr/bin/env python
# coding: utf-8

import sqlite3
import csv
import sys
import argparse


QUERY_TEMPLATE = """
select "COMP Course Number",
       "COMP Section Number",
       "Faculty Last Name",
       Semester,
       Syllabus 
from courses
where Semester="%(qual_semester)s" and "Final Version" == 'Yes'
order by "COMP Course Number";
""".strip()

SYLLABUS_URL_TEMPLATE = """
`%(course_no)s-%(sec_no)s %(faculty_name)s <%(syllabus_url)s>`_
""".strip()

def get_argparse():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        '--db', help='courses database', default='courses.db')
    parser.add_argument(
        '--semester', help='semester (Spring, Summer, Fall) ', required=True)
    parser.add_argument(
        '--year', help='any integer >= 2000', type=int, required=True)
    return parser

def process():
    parser = get_argparse()
    args = parser.parse_args()

    db = sqlite3.connect(args.db)
    cursor = db.cursor()
    semester = args.semester
    year = int(args.year)
    qual_semester = ' '.join([semester,str(year)])
    csv_filename = qual_semester.lower().replace(' ','-') + '.csv'
    results = cursor.execute(QUERY_TEMPLATE % vars())
    print("Writing %s" % csv_filename)
    course_section_map = {}
    with open(csv_filename, 'w') as csvfile:
        spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        for result in results:
            result2 = list(result)
            (course_no, sec_no, faculty_name, semester, syllabus_url) = result2[0:5]
            course_info = { 'course_no' : course_no,
                     'sec_no' : sec_no,
                     'faculty_name' : faculty_name,
                     'semester' : semester,
                     'syllabus_url' : syllabus_url }

            course_sec_key = "%s-%s" % (course_no, sec_no)
            if course_sec_key in course_section_map:
                print("Duplicate: ", course_sec_key, course_info)
                continue
            course_section_map[course_sec_key] = course_info
            annotated_url = SYLLABUS_URL_TEMPLATE % course_info
            spamwriter.writerow([course_sec_key, faculty_name, semester, annotated_url])

if __name__ == '__main__':
    process()
