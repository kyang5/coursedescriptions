These scripts will be used to create the CSV tables for syllabi.

This script gets the CSV version of our Google Sheet containing the course syllabi.
```
$ ./import-courses-csv.sh
```

(See the source code of the script to get an understanding of how to publish a CSV file on Google Sheets.)

This script generates the CSV table for any given semester from the resulting `courses.db` file:

```
$ ./generate-course-csv.py --semester Fall --year 2020
```

This can be automated by CI, but there are some issues:

- CI builds need to be triggered by the Google Sheets (source of truth) changes.
- We don't want the list of syllabi for a given term to change after a certain deadline. We only allow instructors to change syllabi before anything is graded and ask for all syllabi to be finalized by first week of class.
- Most of the needed automation in gathering the syllabi. We only need to add entries to the Sphinx site once a semester.

Please contact gkt@cs.luc.edu with any questions, even if you want to do something similar for your department/university. Happy to show the way!
