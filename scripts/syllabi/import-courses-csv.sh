#!/bin/bash

# Note:
# This link is coming from Google Sheets
# File -> Publish to Web 

echo "Getting Google Sheets Syllabi"

export LINK="https://docs.google.com/spreadsheets/d/e/2PACX-1vT1R7FirTrxj-_gD0LUj_gKPxF9myqvwvxdX109beNrw0wS9P-KI4mGDMEZg1x35w8UrIMNwkx4yDDR/pub?gid=715548665&single=true&output=csv"
wget -O courses.csv "$LINK"

echo "Importing into Local DB"

rm -f courses.db
sqlite3 courses.db << EOF
.mode csv
.import courses.csv courses
.schema
EOF

