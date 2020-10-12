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
where Semester="%(qual_semester)s"
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
    with open(csv_filename, 'w', newline='') as csvfile:
        spamwriter = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
        for result in results:
            result2 = list(result)
            (course_no, sec_no, faculty_name, semester, syllabus_url) = result2[0:5]
            course_info = "%s-%s" % (course_no, sec_no)
            annotated_url = SYLLABUS_URL_TEMPLATE % vars()
            spamwriter.writerow([course_info, faculty_name, semester, annotated_url])

if __name__ == '__main__':
    process()
