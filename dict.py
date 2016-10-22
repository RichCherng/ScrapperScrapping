#!/usr/bin/env python


import sys, os, traceback, urllib2, json, time
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

	content = getPage(strWord)
	if content == None: # Word doesn't exist or cannot request
		dictWordContent  = {}
	else:
		soup = BeautifulSoup(content, 'html.parser')

		#### Thesaurus ###
		thesaurus = soup.findAll("div", { "class" : "deep-link-synonyms" })
		if len(thesaurus) > 0:
			getThesaurus(dictWordContent, thesaurus[0])
		#print mydivs[0].a.get('href')

		### Definition ###
		getDefinition(dictWordContent, soup)

	jsonObject = json.dumps(dictWordContent)
	print jsonObject





## Parsing definition section
#

def getDefinition(_dict, _soup):
	_dict['def'] = {}
	defDiv = _soup.findAll("div", { "class" : "def-list"})
	# defList[0] = definitioni section

	## Sections Of Content ##
	defSection = defDiv[0].findAll("section", {"class" : "def-pbk" })

	for section in defSection:
		# Get category of the section
		category = section.findAll("span", {"class" : "dbox-pg" })
		strCategory = ''
		for string in category:
			strCategory += string.get_text() + ", "
		
		# Get definition of each section
		# for every section, get a list of definitions
		listOfDef = []
		for defContent in section.findAll("div", {"class": "def-content"}):
			listOfDef.append(defContent.get_text())

		_dict['def'][strCategory[:-2]] = listOfDef




## Retrieve Page Content
#  return content of the word in www.dictionary.com

def getPage(_word):
	end = False
	intAttempt = 5;
	strURLAddr = 'http://www.dictionary.com/browse/'+_word
	while not end and intAttempt > 0:
		try:
			response = urllib2.urlopen(strURLAddr)
			end = True
			return response.read()
		except urllib2.URLError:
			print "Retrying on " + _word
			intAttempt -= 1
			time.sleep(1)
		except:
			print 'Error on: ' + _word
			return None
	return None
	
	return response.read()

if __name__ == "__main__":

	# Catch KeyboardInterrupt
	try:
		main()
	except KeyboardInterrupt:
		print ""
	except:
		traceback.print_exc(file=sys.stdout)
		sys.exit()