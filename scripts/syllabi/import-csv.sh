#!/bin/bash

sqlite3 courses.db << EOF
.mode csv
.import courses.csv courses
.schema
select "COMP Course Number" || '-' || "COMP Section Number", "Faculty Last Name", Semester, Syllabus from courses where Semester="Spring 2020" and "Final Version" = 'Yes' order by Semester, "COMP Course Number";
EOF

