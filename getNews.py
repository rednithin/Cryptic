from getNewsInXML import getXML
from lxmlParser import getCSV
from NewsVader import NewsVader
def getNews(coin):
	getXML(coin)
	getCSV(coin)
	NewsVader(coin)
#getNews('Bitcoin')
