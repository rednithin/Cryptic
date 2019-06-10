from RedditScrape import getRedditContent
from RedditVader import RedditVader

def getSubmissions(coin):
	r = getRedditContent(coin)
	if(r==1):
		RedditVader(coin)
		return 1
	else:
		return 0
#getSubmissions('Altcoin')
