#!/usr/bin/env python


import sys, os, traceback, urllib2, json, time,re
from bs4 import BeautifulSoup
#from lxml import etree
#from HTMLParser import HTMLParser
#from lxml import html


def main():

	strWord = sys.argv[1]
	#req = urllib2.Request('http://www.dictionary.com/browse/' + strWord)
	#print req
	#response = urllib2.urlopen(req)
	#the_page = response.read()
	#print the_page
	dictWordContent = { "word": strWord}

	content = getHTML('http://www.dictionary.com/browse/'+ strWord)
	if content == None: # Word doesn't exist or cannot request
		dictWordContent  = {}
	else:
		soupDictionary = BeautifulSoup(content, 'html.parser')

		#### Thesaurus ###
		getThesaurus(dictWordContent, soupDictionary)

		### Definition ###
		getDefinition(dictWordContent, soupDictionary)

		### Get MAP Coords ###
		getMapOrigin(dictWordContent, soupDictionary)

		### Get Origin ###
		getOrigin(dictWordContent, soupDictionary)

		### Get Slang ###
		#getSlang(dictWordContent, soupDictionary)

	jsonObject = json.dumps(dictWordContent)
	print jsonObject


def getOrigin(_dict, _soup):
	_dict['origin'] = {}
	sectionOrigin = _soup.findAll("section", {"id" : "source-etymon2"})
	divSrcBox = sectionOrigin[0].findAll("div", {"class" : "source-box"})

	divDefList = divSrcBox[0].findAll("div", {"class" : "def-list"})
	
	listDef = []
	for defCon in divDefList[0].findAll('div', {"class" : "def-set"}):
		listDef.append(defCon.get_text().replace('\n','').replace('\r', '').lstrip().rstrip())

	_dict['origin']['def'] = listDef


#def getSlang(_dict, _soup):
#	sectionSlang = _soup.findAll("section", {"id": "source-das"})
#	divDefCon = sectionSlang[0].findAll("div", {"class" : "def-con"} )
#	for defCon in divDefCon:
#		for p in defCon.find_all('p'):
#			print p.get_text()
	


##  Get location of origin of the word with their coordinate 
#	@return None

def getMapOrigin(_dict, _soup):
	_dict['MapOriginLocation'] = {}
	divCoords = _soup.findAll("div", {"class": "map-origin-language" ,"style": True})
	for divLocation in divCoords:
		#print divLocation.get_text().rstrip().lstrip()
		_dict['MapOriginLocation'][divLocation.get_text().rstrip().lstrip()] = divLocation['style']
		#print divLocation['style']


	#print divMapOrigin
	


## Retrieve and parse thesaurus page
#  @return None

def getThesaurus(_dict, _soup):
	_dict['thesaurus']	= {}
	divThesaurus 		= _soup.findAll("div", { "class" : "deep-link-synonyms" })
	thesaurusAddr 		= divThesaurus[0].a.get('href')

	if len(thesaurusAddr) > 0:
		# Get HTML of thesaurus
		htmlThesaurusContent  = getHTML(thesaurusAddr)

		# parse thesaurus content
		soupThesaurus 	= BeautifulSoup(htmlThesaurusContent, 'html.parser')
		divSynonyms 	= soupThesaurus.findAll("div", {"class": "synonyms"} )
		
		# Find synonyms
		listSynonyms 	= []
		divRel 			= divSynonyms[0].findAll("div", {"class": "relevancy-block"})
		for a in divRel[0].div.find_all('a'):	
			for text in a.findAll('span', {"class" : "text"}):
				listSynonyms.append(text.get_text())

		_dict['thesaurus']['syn'] = listSynonyms
		_dict['thesaurus']['ant'] = []

		# Find Antonyms
		listAntonyms = []
		devAnt = divSynonyms[0].findAll("section", {"class": "antonyms"})
		ulAnt = devAnt[0].findAll("ul", {"class": "list"})
		if len(devAnt):
			for ul in ulAnt:
				for a in ul.find_all('a'):
					listAntonyms.append(a.get_text())
				

			_dict['thesaurus']['ant'] = listAntonyms


## Parsing definition section
#  @param 
#  @return null

def getDefinition(_dict, _soup):
	_dict['def'] = {}
	defDiv = _soup.findAll("div", { "class" : "def-list"})
	# defList[0] = definitioni section

	## Sections Of Content ##
	defSection = defDiv[0].findAll("section", {"class" : "def-pbk" })

	for section in defSection:
		# Get category of the section
		category 	= section.findAll("span", {"class" : "dbox-pg" })
		strCategory = ''
		for string in category:
			strCategory += string.get_text() + ", "
		
		# Get definition of each section
		# for every section, get a list of definitions
		listOfDef = []
		for defContent in section.findAll("div", {"class": "def-content"}):
			strContent = defContent.get_text().replace('\n','').replace('\r', '').lstrip().rstrip()
			strContent = re.sub(' +', ' ', strContent)
			listOfDef.append(strContent[0].capitalize() + strContent[1:])

		_dict['def'][strCategory[:-2]] = listOfDef




## Retrieve Page Content 
#  @param url address
#  @return HTML as String

def getHTML(_urlAddr):
	end = False
	intAttempt = 5;
	strURLAddr = _urlAddr
	while not end and intAttempt > 0:
		try:
			response = urllib2.urlopen(strURLAddr)
			end = True
			return response.read()
		except urllib2.URLError:
			#print "Retrying on " + _word
			intAttempt -= 1
			time.sleep(1)
		except:
			#print 'Error on: ' + _word
			return None
	return None
	
	return response.read()

if __name__ == "__main__":

	# Catch KeyboardInterrupt
	try:
		main()
	except KeyboardInterrupt:
		#print ""
		pass
	except:
		traceback.print_exc(file=sys.stdout)
		sys.exit()