import os
import csv
import datetime
def parseing(fileName):
	sectionTemplate = '''
:doc:`{subject}{catNumber}`{SpTopic} {Term}
    | Section {section} ({classNumber}) Credits: {units}; {mixture}; {component}
    | Instructor: {Instructor}
    |{Building}:{Room} {Location} {Days} {Time}

	{description}
''' 

	sectionTemplateMultiRoom = '''
:doc:`{subject}{catNumber}`{SpTopic} {Term}
    | Section {section} ({classNumber}) Credits: {units}; {mixture}; {component}
    | Instructor: {Instructor}
    {multiRoom}

	{description}
''' 

	sectionTemplateLab = '''
:doc:`{subject}{catNumber}`{SpTopic} {Term}
    | Section {section}/{labSection} ({classNumber}) Credits: {units}; {mixture}; {component}
    | Instructor: {Instructor}
    |{Building}:{Room} {Location} {Days} {Time}
    |{labBuilding}: {labRoom} ({labLocation}) {labDay} {labTime} (lab)

	{description}
''' 

	comp314_315Template = '''
	{subject} {catNumber} {Term} (Description: :doc:`comp314-315`)
		| Section {section} ({classNumber}) Credits: {units}; {mixture}; {component}
		| Instructor: {Instructor}
	        |{Building}:{Room} {Location} {Days} {Time}

	{description}
	'''

	topicsSectionTemplate = '''
{subject} {catNumber} Topic{topics} {Term}
	| Section {section} ({classNumber}) Credits: {units}; {mixture}; {component}
	| Instructor: {Instructor}
	|{Building}:{Room} {Location} {Days} {Time}
	| Description similar to: :doc:`{docName}`

{description}
'''
	
	headerTemplate = '''
{semester} Schedule {txtURLline} {where}
==========================================================================
{created}

The following courses will (tentatively) be held during the {semester} semester.

For open/full status and latest changes, see
`LOCUS <http://www.luc.edu/locus>`_.

**In case of conflict, information on LOCUS should be considered authoritative.**

See `Textbook Information {textBookURLline}`_.

Section titles lines link to the course description page,
except for some labeled special topics courses related to an existing course.

The 4-digit number in parentheses after the section is the Locus registration code.

Be sure to look at the section's notes or Locus for an 8-week courses with more than one schedule line:
Friday line(s) are likely to be isolated makeup days, not every week.

{graduateLink}

**View Campus Specific Courses below :**
{pages}



.. _{season}_undergraduate_courses_list:

{udergradeTxt}
~~~~~~~~~~~~~~~~~~~~~

'''

	gradHeadingTemplate = '''

.. _{0}_graduate_courses_list_{1}:

Graduate Courses
~~~~~~~~~~~~~~~~~~~~~

'''

	indepStudyTemplate = '''
:doc:`{}` 1-6 credits
	You cannot register
	yourself for an independenst study course!
	You must find a faculty member who
	agrees to supervisor the work that you outline and schedule together.  This
	*supervisor arranges to get you registered*.  Possible supervisors are: full-time department faculty
	'''
	classes = []
	headerObject = {'semester':'', 'textBookURLline':'<https://docs.google.com/spreadsheets/d/138_JN8WEP8Pv5uqFiPEO_Ftp0mzesnEF5IFU1685w3I/edit?usp=sharing>', 
		 'created':'', 'graduateLink':'', 'campusURLTemplateCuneo':'','season':'','udergradeTxt':'Undergraduate Courses', 'where':'', 'pages':'',
		 'txtURLline':''}
	object = {'subject':'','catNumber' : '', 'section':'', 'classNumber':'' , 'title':'','component':'',
	'units':'', 'topics':'', 'Building' : '', 'Location':'', 'Room':'', 'Days':'',
	'Time':'', 'Instructor':'', 'classCap':'','totalStudents':'', 'waitCap':'', 'waitTotal':'', 
	'minEnroll':'', 'Attributes':'', 'roomCharicteristics':'', 'CombinedSID':'', 'ClassEquiv':'', 
	'SpTopic':'', 'Term':'', 'mixture':'', 'description':'', 'hasLab':False, 'labBuilding':'', 'labRoom':'',
	'labTime':'', 'labDay':'', 'labLocation':'', 'Term':'', 'isStudy':False, 'isMultiRoom':False, 'docName':'',
	 'multiRoom':''}
	file = open(fileName, 'r')
	reader = csv.reader(file, delimiter=',')
	LSBuildings = ['Cuneo', 'Mundelein', 'Crown', 'Sullivan', 'Life Science', 'Dumbach']
	checker=0
	string = ''
	appendToList = False
	hasLab = False
	semester = ''
	season = ''
	now = datetime.datetime.now()
	for row in reader:
		#print(row)
		
		for i in range(0, len(row)):
			if "COMP" == row[0]:
				object['subject'] = row[i].lower()
				object['catNumber'] = row[i+1]
				if object['catNumber'] == '398':
					object['isStudy'] = True
				object['section'] = row[i+2]
				if 'L' in row[i+2]:
					for m in range(0,len(classes)):
						if classes[m]['catNumber'] == object['catNumber'] and classes[m]['section'] in object['section']:
							classes[m]['hasLab'] = True
							hasLab = True
							classes[m]['labSection'] = row[i+2]
				else:
					object['section'] = row[i+2]
							
				object['classNumber'] = row[i+3]
				object['title'] = row[i+4]
				object['component'] = row[i+5]
				object['units'] = row[i+6]
				if i+7 <= len(row):
					object['topics'] = row[i+7]
					break
				break
			elif " Fall " in row[0]:
				semester = "Fall " + str(now.year)
				season = 'Fall'
				headerObject['season'] = season
				headerObject['semester']= semester
			elif " Spring " in row[0]:
				semester = "Spring " + str(now.year)
				season = 'Spring'
				headerObject['season'] = season
				headerObject['semester']= semester
			elif 'Week' in row[0]:
				object['Term'] = "[" + str(row[0]) + "]"
			elif row[0] == 'Bldg:' and not hasLab:
				if object['Building'] != '':
					object['Building'] = object['Building'] + ' +' +str(row[i+1])
					object['Room'] = object['Room'] +' + '+row[i+3]
					object['Days']= object['Days'] +' + '+convertDays(row[i+5])
					object['Time'] = object['Time'] +' + '+row[i+7]
					for j in range(0, len(LSBuildings)):
						if LSBuildings[j] in row[i+1]:
							object['Location'] = '(Lake Shore)' + ' +' + object['Location']
							break
						if row[i+1] == 'TBA':
							object["Location"] = '' + ' + ' + object['Location']
							break
						if row[i+1] == 'Online':
							object['Location'] =  '(Online)' + ' +' + object['Location']
							break
						if j == len(LSBuildings)-1:
							object['Location'] = '(Water Tower)' + ' +' + object['Location'] 
						  
					object['isMultiRoom'] = True
				else:
					object['Building'] = row[i+1]
					object['Room'] = row[i+3]
					object['Days']= convertDays(row[i+5])
					object['Time'] = row[i+7]
					if 9 < len(row):
						object['Instructor'] = row[9]
					for j in range(0, len(LSBuildings)):
						if LSBuildings[j] in object['Building']:
							object['Location'] = '(Lake Shore)'
							break
						elif object["Building"] == 'TBA':
							object["Location"] = ''
							break
						elif object['Building'] == 'Online':
							object['Location'] = '(Online)'
							break
						else:
							object['Location'] = '(Water Tower)'
				if object['Instructor'] == '':
					object['Instructor'] = 'N/A'
				break
			elif row[0] == 'Bldg:' and hasLab:
				for m in range(0,len(classes)):
					if classes[m]['catNumber'] == object['catNumber'] and classes[m]['section'] in object['section']:
						classes[m]['labBuilding'] = row[i+1]
						waterTower = True
						for j in range(0, len(LSBuildings)):
							if LSBuildings[j] in classes[m]['labBuilding']:
								classes[m]['labLocation'] = 'Lake Shore'
								waterTower = False
							elif classes[m]["labBuilding"] == 'TBA':
								classes[m]["labLocation"] = ''
								waterTower = False
							elif classes[m]['labBuilding'] == 'Online':
								classes[m]['labLocation'] = 'Online'
								waterTower = False
						if waterTower:
							classes[m]['labLocation'] = 'Water Tower'
							
								
						classes[m]['labRoom'] = row[i+3]
						classes[m]['labDay']= convertDays(row[i+5])
						classes[m]['labTime'] = row[i+7]	
				break
			elif row[0] == 'Class Enrl Cap:':
				object['classCap'] = row[i+1]
				object['totalStudents'] = row[i+3]
				object['waitCap'] = row[i+5]
				object['waitTotal'] = row[i+7]
				if i+9 < len(row[i]):
					object['minEnroll'] = row[i+9]
					break
				break	
			elif row[0] == 'Attributes:':
				object['Attributes'] = row[1]
			elif row[0] == 'Room Characteristics:':
				object['roomCharicteristics'] = row[i+1]
				break
			elif row[0] == "Class Equivalents:":
				if len(row) > i+1:
					object['ClassEquiv'] = row[i+1]
			elif 'Combined with' in row[0]:
				tempList = row[0].split()
				for q in range(0,len(tempList)):
					if 'COMP' == tempList[q]:
						tempSplit = tempList[q+1].split('-')
						classNum = tempSplit[0]
						object['docName'] = tempList[q].lower() + classNum
			elif '_______' in row[0]:
				if string != '':
					object['description'] = "**Notes**\n        " + string
				string = ''
				if hasLab == False:
					appendToList = True
				hasLab = False
				break
			elif row[0] == 'Combined Section ID:':
				object['CombinedSID'] == row[1] + row[2]+row[3]
				break
			elif row[0] == '':
				for q in range(0,len(row)):
					if row[q] != '':
						object['mixture'] = row[q]
					
			else:
				if row[i] != '':
					string +=  row[i] + '\n        '
		if appendToList:
			if 'Report ID:' not in object['description']:
				classes.append(object)
				#print(object)
				#print(len(classes))
			elif object['isStudy']:
				continue
				
			object = object.fromkeys(object, '')
			appendToList = False
			object['Building'] = ''
			object['Days'] = ''
			object['Room'] = ''
			object['Days']= ''
			object['Time'] = ''
			object['Location'] = ''
	mainRST = open(season+'.rst','w')
	onlineRST = open('online'+season+'.rst','w')
	lakeRST = open('lakeShore'+season+'.rst','w')
	waterRST = open('waterTower'+season+'.rst','w')
	headerObject['pages'] = '''
	:doc:`lakeShore{0}`

	:doc:`waterTower{0}`

	:doc:`online{0}`'''.format(season)
	mainRST.write(headerTemplate.format(**headerObject))
	headerObject['where'] = '(Lake Shore)'
	headerObject['pages'] = '''
	:doc:`{0}`

	:doc:`waterTower{0}`

	:doc:`online{0}`'''.format(season)
	lakeRST.write(headerTemplate.format(**headerObject))
	headerObject['where'] = '(Online)'
	headerObject['pages'] = '''
	:doc:`lakeShore{0}`

	:doc:`waterTower{0}`

	:doc:`{0}`'''.format(season)
	onlineRST.write(headerTemplate.format(**headerObject))
	headerObject['where'] = '(Water Tower)'
	headerObject['pages'] = '''
	:doc:`lakeShore{0}`

	:doc:`{0}`

	:doc:`online{0}`'''.format(season)
	waterRST.write(headerTemplate.format(**headerObject))
	Check398 = True
	Check499 = True
	Check490 = True
	for k in range(0, len(classes)):
		currentLine = ''
		if classes[k]['hasLab']:
			currentLine = sectionTemplateLab.format(**classes[k])
		elif classes[k]['isMultiRoom']:
			multiRoom = ''
			bList = classes[k]['Building'].split('+')
			dList = classes[k]['Days'].split('+')
			rList = classes[k]['Room'].split('+')
			lList = classes[k]['Location'].split('+')
			tList = classes[k]['Time'].split('+')
			for times in range(0, len(bList)):
				multiRoom = multiRoom + "| {0}: {1} {2} {3} {4} \n    ".format(bList[times], rList[times],lList[times],dList[times],tList[times])
			classes[k]['multiRoom'] = multiRoom
			currentLine = sectionTemplateMultiRoom.format(**classes[k])
		elif classes[k]['catNumber'] == '314' or classes[k]['catNumber'] == '315':
			currentLine = comp314_315Template.format(**classes[k])
		elif classes[k]['catNumber'] == '388' or classes[k]['catNumber'] == '488':
			currentLine = topicsSectionTemplate.format(**classes[k])
		elif '398' in classes[k]['catNumber']  or '499' in classes[k]['catNumber'] or '490' in classes[k]['catNumber'] :
			if '398' in classes[k]['catNumber'] :
				if Check398:
					currentLine = indepStudyTemplate.format("398")
					Check398 = False
				else:
					currentLine = 0
			if '490' in classes[k]['catNumber'] :
				if Check499:
					currentLine = indepStudyTemplate.format("499")
					Check499 = False
				else:
					currentLine = 0
			if '499' in classes[k]['catNumber']:
				if Check490:
					currentLine = indepStudyTemplate.format("490")
					Check490 = False
				else:
					currentLine = 0
		else:
			currentLine = sectionTemplate.format(**classes[k])
		createHeading = False
		if int(classes[k-1]['catNumber']) < 400 and int(classes[k]['catNumber']) >= 400:
			createHeading = True
			
		if currentLine != 0:
			if 'Lake' in classes[k]['Location']:
				if createHeading:
					lcurrentLine = gradHeadingTemplate.format(season, 'Lake Shore') + '\n' + currentLine
					lakeRST.write(lcurrentLine+'\n')
				else:
					lakeRST.write(currentLine+'\n')
			if 'Water' in classes[k]['Location']:
				if createHeading:
					wcurrentLine = gradHeadingTemplate.format(season, 'Water Tower') + '\n' + currentLine
					waterRST.write(wcurrentLine+'\n')
				else:
					waterRST.write(currentLine+'\n')
			if 'Online' in classes[k]['Location']:
				if createHeading:
					ocurrentLine = gradHeadingTemplate.format(season, 'Online') + '\n' + currentLine
					onlineRST.write(ocurrentLine+'\n')
				else:
					onlineRST.write(currentLine+'\n')
			if createHeading:
				fcurrentLine = gradHeadingTemplate.format(season, 'Fall') + '\n' + currentLine
				mainRST.write(fcurrentLine+'\n')
			else:
				mainRST.write(currentLine+'\n')	
	
	mainRST.close()
	onlineRST.close()
	lakeRST.close()
	waterRST.close()

def convertDays(days):
	if days == 'M':
		return 'Monday'
	if days == 'Tu':
		return 'Tuesday'
	if days == 'W':
		return 'Wednesday'
	if days == 'Th':
		return 'Thursday'
	if days == 'F':
		return 'Friday'
	if days == 'Sa':
		return 'Saturday'
	if days == 'MWF':
		return 'Monday, Wednesday, Friday'
	if days == 'TuTh':
		return 'Tuesday, Thursday'
	if days == 'MW':
		return 'Monday, Wednesday'
	
name = input("Enter file name.")
parseing(name) 