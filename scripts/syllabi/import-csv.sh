#!/bin/bash

sqlite3 courses.db << EOF
.mode csv
.import courses.csv courses
.schema
select * from courses;
EOF
