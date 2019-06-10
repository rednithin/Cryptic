from getCSV import getCSV
from TwitterVader import TwitterVader

def getTweets(coin):
	getCSV(coin)
	TwitterVader(coin)

#getTweets('Ethereum')
