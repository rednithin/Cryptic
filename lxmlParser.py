import os
from lxml import etree
def getCSV(coin):
	try:
		os.remove("/home/nithin/Git/Cryptic/SentimentAnalysis/News/CSV/"+coin+"NewsValid.csv")
	except OSError:
		pass
	fhand = open("/home/nithin/Git/Cryptic/SentimentAnalysis/News/CSV/"+coin+"NewsValid.csv","w")
	infile = "/home/nithin/Git/Cryptic/SentimentAnalysis/News/XML/"+coin+"NewsValid.xml"
	context = etree.iterparse(infile,events = ('end',),tag = 'item')	#finds all item tags and creates a tree for each item tag. Once parsed, it takes the next item tag to parse
	#counter = 1
	fhand.write("Article\n")
	for event,tags in context:
		#print(counter)
		#counter+=1
		data = ""
		for child in tags:
			if child.tag == "title":
				#data += child.text
				#data += "\t"
				pass
			elif child.tag == "description":
				data += child.text
		#print(data)
		fhand.write(data)
		#if(counter == 5):
		#	break
#getCSV('Bitcoin')	
