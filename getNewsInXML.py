import urllib.request
import os
from urllib.request import Request, urlopen

#url = "https://www.ccn.com/crypto/feed"
#url = "https://www.ccn.com/tag/bitcoin/feed"
#url = "https://www.ccn.com/tag/ethereum/feed"
#url = "https://www.ccn.com/tag/litecoin/feed"
#url = "https://www.ccn.com/tag/altcoin/feed"
#url = "https://www.ccn.com/tag/satoshi/feed"
#url = "https://www.ccn.com/tag/ico/feed"
#url = "https://www.ccn.com/tag/mining/feed"
#url = "https://www.ccn.com/tag/wallet/feed"
#url = "https://www.ccn.com/tag/CoinBase/feed"
#url = "https://www.ccn.com/tag/Poloniex/feed"
#url = "https://www.ccn.com/tag/binance/feed"
#url = "https://www.ccn.com/news/feed"

def getXML(coin):
	url = "https://www.ccn.com/tag/"+coin+"/feed"
	req = Request(url, headers={'User-Agent': 'Mozilla/5.0'})
	webpage = urlopen(req).read()
	#url = "https://www.ccn.com/crypto/feed"

	#s = urllib.request.urlopen(url)
	#contents = s.read()
	try:
		os.remove("/home/nithin/Git/Cryptic/SentimentAnalysis/News/XML/"+coin+"NewsValid.xml")
	except OSError:
		pass
	file = open("/home/nithin/Git/Cryptic/SentimentAnalysis/News/XML/"+coin+"NewsValid.xml","wb")
	file.write(webpage)
	file.close()

#getXML('Bitcoin')
#print("done")
