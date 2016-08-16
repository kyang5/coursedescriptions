'''script to take csv file from Locus class cedule and make
nice .rst file <semester>.rst'''

from csv import reader

##example:
##    ['____________________________ ... ', '']
##    ['COMP', ' 150', '002', '3450', 'Introduction to Computing', 'Lecture', '3', '', '']
##    ['', '', '', '', '', '', '(In person)']
##    ['Bldg:', 'Crown Center', 'Room:', '105', 'Days:', 'MW', 'Time:', '04:15PM-05:30', '', 'Instructor:', 'Tuckey,Curtis D']
##    ['Class Enrl Cap:', '25', 'Class Enrl Tot:', '8', 'Class Wait Cap:', '0', 'Class Wait Tot:', '0', 'Class Min Enrl:', '0']
##    ['Class Equivalents:', 'ACCOMP 150/COMP 150']
##    []
##    ['This course is restricted to undergraduate students.']
##    ['Graduate students wishing to enroll in a section of this course should contact their departmental']
##    ['graduate advisor.']
##    ['_________________________________________________ ... ', '']
##    ['', '', '', '', '', '', '', '', '']
##    ['Report ID:  SR201', 'Loyola University Chicago', 'Page No.', '4', 'of', '25']
##    ['Schedule of Classes for Fall 2016', 'Run Date:', '05/13/2016']
##    ['Campus: Lake Shore Campus   Location: Lake Shore Campus', 'Run Time:', '22:28:26']
##    ['', '', '', '', '', '', 'Regular Academic Session']
##    ['College of Arts and Sciences - Computer Science - Subject: Computer Science']
##    []
##    ['____________________________________________________ ... ',
##     'Subject', 'Catalog Nbr', 'Section', 'Class Nbr', 'Course Title', 'Component', 'Units', 'Topics']

logList = []

def log(s):
    logList.append(s)

def printLog():
    if logList:
        print('\n\nLogged items: ')
        for s in logList:
            print(s)

def joinIndented(lines, indent):
    'lines is a list of lines.  Return lines indented in one string'
    if not lines:  return ''
    lines = [indent + line.strip() for line in lines]
    return '\n'.join(lines)


sectionTemplate = '''
:doc:`{docName}`{topic} {term}
    | Section {section} ({regCode}) Credits: {credits}; {mixture}; {format}
    | Instructor: {instructor}
{placeTimes}

{notes}
''' # docName link should give full course title

comp314_315Template = '''
{area} {number} {term} (Description: :doc:`comp314-315`)
    | Section {section} ({regCode}) Credits: {credits}; {mixture}; {format}
    | Instructor: {instructor}
{placeTimes}

{notes}
'''

topicsSectionTemplate = '''

{area} {number} Topic{topic} {term}
    | Section {section} ({regCode}) Credits: {credits}; {mixture}; {format}
    | Instructor: {instructor}
{placeTimes}
    | Description similar to: :doc:`{docName}`

{notes}
'''

class Section:
    '''Has members (example in paren)
      campus (Online, Lakshore, Watertower, Cuneo)
      term  (regular is '', 8 Week 1)
      instructor (Willaim Honig)
      instructorList(['Honig, William'])
      area (COMP)
      number (170)
      section (002 or 02L)
      regCode (4235)
      title (Introduction to Computing) not used, but check?
      format (Lecture or Laboratory)
      credits (3 or 1-6)
      topic (Foundations of Computer Science I - for 388, 488)
      mixture (In person, Hybrid, Online)
      placeTimes (indented string lines from list of place-days-time-campus)
      notes (indented string of lines)
      crsAbbr (comp150)
      abbr (comp150-001) 
      docName (comp150 or special for topics course section))
    '''
    def __init__(self, campus, term, lines, indent = ' '*4):
        self.campus = campus
        self.term = term
        if lines[2][-1].strip() != 'Instructor:': # may be no field for instructor
            firstInstructor = lines[2][-1]
        else:
            firstInstructor = 'Staff'
        self.instructorList = [firstInstructor]
        self.area = lines[0][0].strip()
        if self.area != 'COMP':
            log('bad line 0:', line[0])
        self.number = lines[0][1].strip()
        self.section = lines[0][2].strip()
        self.regCode = lines[0][3].strip()
        self.title = lines[0][4].strip()
        self.format = lines[0][5].strip()
        self.credits = lines[0][6].strip()
        self.topic = lines[0][7].strip()
        if self.topic:  self.topic = ': ' + self.topic
        self.mixture = lines[1][-1].strip()[1:-1]
        self.crsAbbr = self.area.lower() + self.number
        self.abbr = self.crsAbbr + '-' + self.section
        self.setDocName() 
        placeTimeList = [] #allow multiple lines
        i = 2
        lastFriLoc = ''
        while lines[i] and lines[i][0] == 'Bldg:':
            loc = getPlaceTime(lines[i], campus)
            # assume short term Fridays as later entrues are special, not all term.
            if i>2 and self.term and ', Friday' not in loc and 'Friday' in loc:
                if lastFriLoc != loc:
                    placeTimeList.append(loc + ' - Check week(s)')
                lastFriLoc = loc
            else:
                placeTimeList.append(loc)
            i += 1
            if len(lines[i-1]) == len(lines[i]) and not lines[i][0]: # further instr under orig, empty fields before
                if lines[i][-1] and lines[i][-1] not in self.instructorList:
                     self.instructorList.append(lines[i][-1])
                i += 1
                                                                  
        lastFriLoc = ''
        self.placeTimes = joinIndented(placeTimeList, indent + '| ')  # force separate lines
        self.instructorList.sort()
        self.instructor = ', '.join([parse_instructor(instr) for instr in self.instructorList])
        if lines[i] and lines[i][0] == 'Class Enrl Cap:': #look for more unused line types in future
            i += 1
        if lines[i] and lines[i][0] == 'Class Equivalents:':
            i += 1
        if lines[i] and lines[i][0]: # skip seq of empty columns
            i += 1
        notes = [line[0] if line else '' for line in lines[i:-1] ] # skip dashes line at end
        if notes:
            notes[0] = '**Notes:** ' + notes[0].strip()
        self.notes = joinIndented(notes, indent).rstrip()

    def setDocName(self):
        #assume convention for section > 100, section is corresponding linked course
        specialSect = {'502': '305'
                      }
        self.docName = self.crsAbbr
        if self.crsAbbr in ['comp388', 'comp488']:
            if specialSect.get(self.section):
                self.docName = 'comp' + specialSect[self.section]
            elif self.section >= '100':
                self.docName = 'comp' + self.section 

                
    def toRST(self):
        if self.crsAbbr in ['comp314', 'comp315']:
            return comp314_315Template.format(**self.__dict__)
        if self.crsAbbr == self.docName:
            return sectionTemplate.format(**self.__dict__)
        return topicsSectionTemplate.format(**self.__dict__)

    def __lt__(self, other):
        return self.abbr < other.abbr

                                   
def getPlaceTime(line, campus):
    'Return string for place, time, campus; online, TBA treated specially'
    bldg = line[1].strip()
    room = line[3].strip()
    days = parse_days(line[5])
    clock = line[7].strip()
    if clock == 'TBA':
        time = 'Times: TBA'
    else:
        time = days + ' ' + clock
    if campus == 'Online':
        return 'Online ' + time
    if room == 'TBA':
        place = 'Place TBA'
    else:
        place = bldg+ ':' + room
    return '{} ({}) {}'.format(place, campus, time)
    
def parse_days(days):
    'Remove day abbreviations: MWF -> Monday, Wednesday, Friday'
    days = days.strip()
    if days in ['See Note', 'TBA']:
       return days
    orig = days
    full = []
    for (abbr, day) in [('M', 'Monday'), ('Tu', 'Tuesday'), ('W', 'Wednesday'),
                            ('Th', 'Thursday'), ('F', 'Friday'), ('Sa', 'Saturday')]:
        if abbr in days:
            full.append(day)
            days = days.replace(abbr, '')
    if days or not orig:
        log('Bad days code ' + orig)
        return 'TBA'
    return ', '.join(full)

# decodes the instructor names putting them in order: "Smith,Adam" = Adam Smith
def parse_instructor(instructor):
    parts = instructor.split(',')
    if '' in parts:
        return 'TBA'
    else:
        parts.reverse()
        return ' '.join(parts)


headingTemplate = '''
{semester} Schedule {textURLline}
==========================================================================
{created}

The following courses will (tentatively) be held during the {semester} semester.

For open/full status and latest changes, see 
`LOCUS <http://www.luc.edu/locus>`_.

**In case of conflict, information on LOCUS should be considered authoritative.**

{txtBookURLline}

Section titles lines link to the course description page, 
except for some labeled special topics courses related to an existing course.

The 4-digit number in parentheses after the section is the Locus registration code.

Be sure to look at the section's notes or Locus for an 8-week courses with more than one schedule line:
Friday line(s) are likely to be isolated makeup days, not every week.

{graduateLink}

**View Campus Specific Courses below :**
{campusURLTemplateCuneo}



.. _{season}_undergraduate_courses_list:

{udergradeTxt}
~~~~~~~~~~~~~~~~~~~~~

'''

gradHeadingTemplate = '''        

.. _{season}_graduate_courses_list_{mainCampus}:

Graduate Courses
~~~~~~~~~~~~~~~~~~~~~

'''

indepStudyTemplate = '''
:doc:`{}` 1-6 credits
    You cannot register 
    yourself for an independent study course!
    You must find a faculty member who
    agrees to supervisor the work that you outline and schedule together.  This
    *supervisor arranges to get you registered*.  Possible supervisors are: {}
'''

def doIndepStudyRST(crsAbbr, courses):
    names = []
    for section in courses:
        if courses[section].crsAbbr == crsAbbr:
           names += courses[section].instructorList
    names = [name for name in names if name != 'Staff']
    names.sort()  # name last-first for sorting
    names = [parse_instructor(name) for name in names]
    return indepStudyTemplate.format(crsAbbr, ', '.join(names))  

def fixLabs(courses):
    for name, sect in list(courses.items()):
        if sect.section.endswith('L'):
            mainAbbr = name.replace('-', '-0')[:-1] # comp170-02L -> comp170-002
            mainSect = courses.get(mainAbbr)
            if mainSect:
                mainSect.format += '/Lab'
                mainSect.placeTimes += '\n' + sect.placeTimes + ' (lab)'
                mainSect.section += '/' + sect.section
                del(courses[name])

def doLevelRST(names, indep, rstParts, courses):
    'Assemble grad or undergrad part with special independent study entry'
    for sect in names:
        if sect == indep:
            rstParts.append(doIndepStudyRST(sect, courses))
        course = courses.get(sect) 
        if course:  # so not deleted lab section
            rstParts.append(course.toRST())    

def toRST(courses, semester, created, mainCampus, textURL=''):
    'return the entire rst file contents'
    undergrad = ['comp398'] + [section for section in courses   # one placeholder for 398
                               if courses[section].area == 'COMP' and 
                                  '398' != courses[section].number < '400']
    undergrad.sort() 

    fixLabs(courses) # need if stupid separate lab sections
    grad = ['comp490'] + [section for section in courses  # one placeholder for 490
                          if courses[section].area == 'COMP' and 
                             '490' != courses[section].number >= '400']
    grad.sort() 

    # later CSIS, too?

    season = semester.split()[0]
    txtBookURLTemplate= '''See `Textbook Information <{textURL}>`_.'''
    txtBookURLline = txtBookURLTemplate.format(**locals()) if textURL else ''
    textURLTemplate= '''( `{mainCampus}` Campus )'''
    textURLline = textURLTemplate.format(**locals()) if mainCampus else ''
    campusURLTemplate= ''' 
:doc:`lakeShorefall`

:doc:`waterTowerFall`

:doc:`cuneoFall`

:doc:`onlineFall` '''
    campusURLTemplateCuneo= ''' 
:doc:`lakeShorefall`

:doc:`waterTowerFall`

:doc:`onlineFall` '''
    graduateLink = '''
You can skip down to
:ref:`fall_graduate_courses_list_`. '''
    udergradeTxt = 'Undergraduate Courses'
    parts = [headingTemplate.format(**locals())]
    
    doLevelRST(undergrad, 'comp398', parts, courses)
    parts.append(gradHeadingTemplate.format(**locals()))
    doLevelRST(grad, 'comp490', parts, courses)
    
    return '\n'.join(parts)



def toLSRST(courses, semester, created, mainCampus, textURL=''):
    'return the entire rst file contents'
    undergrad = ['comp398'] + [section for section in courses   # one placeholder for 398
                               if courses[section].area == 'COMP' and 
                                  '398' != courses[section].number < '400' and 
                                  courses[section].campus == 'Lake Shore']
    undergrad.sort() 

    fixLabs(courses) # need if stupid separate lab sections
    grad = ['comp490'] + [section for section in courses  # one placeholder for 490
                          if courses[section].area == 'COMP' and 
                             '490' != courses[section].number >= '400' and 
                                  courses[section].campus == 'Lake Shore']
    grad.sort() 

    # later CSIS, too?
    mainCampus = 'Lake Shore'
    season = semester.split()[0]
    txtBookURLTemplate= '''See `Textbook Information <{textURL}>`_.'''
    txtBookURLline = txtBookURLTemplate.format(**locals()) if textURL else ''
    textURLTemplate= '''( {mainCampus} Campus )'''
    textURLline = textURLTemplate.format(**locals()) if mainCampus else ''
    campusURLTemplate= ''' 
:doc:`fall`

:doc:`waterTowerFall`

:doc:`cuneoFall`

:doc:`onlineFall` '''
    campusURLTemplateCuneo= ''' 
:doc:`fall`

:doc:`waterTowerFall`

:doc:`onlineFall` '''
    graduateLink = '''
You can skip down to
:ref:`fall_graduate_courses_list_Lake Shore`. '''
    udergradeTxt = 'Undergraduate Courses'
    parts = [headingTemplate.format(**locals())]
    
    doLevelRST(undergrad, 'comp398', parts, courses)
    parts.append(gradHeadingTemplate.format(**locals()))
    doLevelRST(grad, 'comp490', parts, courses)
    return '\n'.join(parts)

def toWTRST(courses, semester, created, mainCampus, textURL=''):
    'return the entire rst file contents'
    undergrad = ['comp398'] + [section for section in courses   # one placeholder for 398
                               if courses[section].area == 'COMP' and 
                                  '398' != courses[section].number < '400' and 
                                  courses[section].campus == 'Water Tower']
    undergrad.sort() 

    fixLabs(courses) # need if stupid separate lab sections
    grad = ['comp490'] + [section for section in courses  # one placeholder for 490
                          if courses[section].area == 'COMP' and 
                             '490' != courses[section].number >= '400' and 
                                  courses[section].campus == 'Water Tower']
    grad.sort() 

    # later CSIS, too?
    mainCampus = 'Water Tower'
    season = semester.split()[0]
    txtBookURLTemplate= '''See `Textbook Information <{textURL}>`_.'''
    txtBookURLline = txtBookURLTemplate.format(**locals()) if textURL else ''
    textURLTemplate= '''( {mainCampus} Campus )'''
    textURLline = textURLTemplate.format(**locals()) if mainCampus else ''
    campusURLTemplate= ''' 
:doc:`fall`

:doc:`lakeShorefall`

:doc:`cuneoFall`

:doc:`onlineFall` '''
    campusURLTemplateCuneo= ''' 
:doc:`fall`

:doc:`lakeShorefall`

:doc:`onlineFall` '''
    graduateLink = '''
You can skip down to
:ref:`fall_graduate_courses_list_Water Tower`. '''
    udergradeTxt = 'Undergraduate Courses'
    parts = [headingTemplate.format(**locals())]
    
    doLevelRST(undergrad, 'comp398', parts, courses)
    parts.append(gradHeadingTemplate.format(**locals()))
    doLevelRST(grad, 'comp490', parts, courses)
     
    return '\n'.join(parts)

def toCuneoRST(courses, semester, created, mainCampus, textURL=''):
    'return the entire rst file contents'
    undergrad = [section for section in courses   # one placeholder for 398
                               if courses[section].area == 'COMP' and 
                                  '398' != courses[section].number < '400' and 
                                  courses[section].campus == 'Cuneo Mansion']
    undergrad.sort() 

    fixLabs(courses) # need if stupid separate lab sections
    grad = ['comp490'] + [section for section in courses  # one placeholder for 490
                          if courses[section].area == 'COMP' and 
                             '490' != courses[section].number >= '400' and 
                                  courses[section].campus == 'Cuneo Mansion']
    grad.sort() 

    # later CSIS, too?
    mainCampus = 'Cuneo Mansion'
    season = semester.split()[0]
    txtBookURLTemplate= '''See `Textbook Information <{textURL}>`_.'''
    txtBookURLline = txtBookURLTemplate.format(**locals()) if textURL else ''
    textURLTemplate= '''( {mainCampus} Campus )'''
    textURLline = textURLTemplate.format(**locals()) if mainCampus else ''
    campusURLTemplate= ''' 
:doc:`fall`

:doc:`lakeShorefall`

:doc:`waterTowerFall`

:doc:`onlineFall` '''
    campusURLTemplateCuneo = ''
    graduateLink = ''
    udergradeTxt = ''
    parts = [headingTemplate.format(**locals())]
    
    doLevelRST(undergrad, 'comp398', parts, courses)
    parts.append(gradHeadingTemplate.format(**locals()))
    doLevelRST(grad, 'comp490', parts, courses)
    
    return '\n'.join(parts)

def toOnlineRST(courses, semester, created, mainCampus, textURL=''):
    'return the entire rst file contents'
    undergrad = ['comp398'] + [section for section in courses   # one placeholder for 398
                               if courses[section].area == 'COMP' and 
                                  '398' != courses[section].number < '400' and 
                                  courses[section].campus == 'Online']
    undergrad.sort() 

    fixLabs(courses) # need if stupid separate lab sections
    grad = ['comp490'] + [section for section in courses  # one placeholder for 490
                          if courses[section].area == 'COMP' and 
                             '490' != courses[section].number >= '400' and 
                                  courses[section].campus == 'Online']
    grad.sort() 

    # later CSIS, too?
    mainCampus = 'Online'
    season = semester.split()[0]
    txtBookURLTemplate= '''See `Textbook Information <{textURL}>`_.'''
    txtBookURLline = txtBookURLTemplate.format(**locals()) if textURL else ''
    textURLTemplate= '''( {mainCampus} Courses )'''
    textURLline = textURLTemplate.format(**locals()) if mainCampus else ''
    campusURLTemplate= ''' 
:doc:`fall`

:doc:`lakeShorefall`

:doc:`waterTowerFall`

:doc:`cuneoFall` '''
    campusURLTemplateCuneo= ''' 
:doc:`fall`

:doc:`lakeShorefall`

:doc:`waterTowerFall` '''
    graduateLink = '''
You can skip down to
:ref:`fall_graduate_courses_list_Online`. '''
    udergradeTxt = 'Undergraduate Courses'
    parts = [headingTemplate.format(**locals())]
    
    doLevelRST(undergrad, 'comp398', parts, courses)
    parts.append(gradHeadingTemplate.format(**locals()))
    doLevelRST(grad, 'comp490', parts, courses)
    
    return '\n'.join(parts)
def printLines(lines, n):
    'front n > 0; end, backwards, n <0'
    if n >0:
        n = min(n, len(lines))
        print('\nprinting', n, 'lines:')
        for line in lines[:n]:
            print(line)
    else:
        n = min(-n, len(lines))
        print('\nprinting', n, 'lines from end back:')
        for line in lines[-1:-n-1:-1]:
            print(line)
        
def getLines(rawLines):
    '''return csv list of entries for each line,
    If rawLines is a string it is taken as a csv file name'''
    if isinstance(rawLines, str):
        with open(rawLines) as inf:
            lines = list(reader(inf))
        #printLines(lines, 15)
        return lines
    return list(reader(rawLines))


def isDashes(s):
    return s.startswith('_____________')

def getToDashes(lines):
    part = []
    while lines:
        line = lines.pop()
        part.append(line)
        if line and isDashes(line[0]):
            return part       
    return None


def parseCSV(csvFile):
    '''return dictionary of courses, semester heading data'''
    #ToDo: check fits assumed format
    lines = getLines(csvFile)
    lines.reverse()
    #printLines(lines, -15) #DEBUG
    courses = {}
    campus = 'Not set'
    term = 'Not set'
    semester = 'Not set'
    created = 'Not set'
    mainCampus = ''
     
    while(lines):
        part = getToDashes(lines)
        if part is None:
            #print('At end!') #DEBUG
            return (courses, semester, created, mainCampus)
        #print('Current section: ') #DEBUG
        #for line in part: #DEBUG
        #    print(line)
        if part[-1][-1] == 'Topics': # page header
            if not part[0][0]:  #empty commas at start for all but first page
                part = part[1:]
            #print('Parsing page', part[0][3], 'semester', part[1][0]) #DEBUG
            semester = ' '.join(part[1][0].split()[-2:]) # last two words of first entry in second line
            date = part[1][2]
            time = part[2][2]
            campus = part[2][0].partition('Location')[0].strip().replace('Campus: ', '').replace(' Campus', '')
            # assume campus and location same?
            term = part[3][0] # empty string for regular session
            
            if term:
                term = '[Term: ' + term + ']'
            created = 'Updated {} {}'.format(date, time)
            if not term and part[3][6] != 'Regular Academic Session':
               term = '[Term: ' + part[3][6] + ']'
        else:  # section description
            #print('Processing section') #DEBUG
            section = Section(campus, term, part)
            courses[section.abbr] = section
        #input('press return: ')  #DEBUG

def main():
    (courses, semester, created, mainCampus) = parseCSV('fall2016.csv')
    rst = toRST(courses, semester, created, mainCampus, textURL='https://drive.google.com/file/d/0B-fjZsnF5rfKbVlxZXVXV2dCejg/view?usp=sharing')
    printLog()
    with open('source/fall.rst', 'w') as outf:
        outf.write(rst)
##    if sys.args
#RST file for Lake shore Campus
    lsrst = toLSRST(courses, semester, created, mainCampus, textURL='https://drive.google.com/file/d/0B-fjZsnF5rfKbVlxZXVXV2dCejg/view?usp=sharing')
    printLog()
    with open('source/lakeShoreFall.rst', 'w') as outf:
        outf.write(lsrst)
#RST file for Water Tower Campus
    wtrst = toWTRST(courses, semester, created, mainCampus, textURL='https://drive.google.com/file/d/0B-fjZsnF5rfKbVlxZXVXV2dCejg/view?usp=sharing')
    printLog()
    with open('source/waterTowerFall.rst', 'w') as outf:
        outf.write(wtrst)
#RST file for Cuneo Courses
    cuneorst = toCuneoRST(courses, semester, created, mainCampus, textURL='https://drive.google.com/file/d/0B-fjZsnF5rfKbVlxZXVXV2dCejg/view?usp=sharing')
    printLog()
    with open('source/cuneoFall.rst', 'w') as outf:
        outf.write(cuneorst)
#RST file for Online Courses
    onlinerst = toOnlineRST(courses, semester, created, mainCampus, textURL='https://drive.google.com/file/d/0B-fjZsnF5rfKbVlxZXVXV2dCejg/view?usp=sharing')
    printLog()
    with open('source/onlineFall.rst', 'w') as outf:
        outf.write(onlinerst)

main()
