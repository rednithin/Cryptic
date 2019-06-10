import tweepy
import csv
import re
import pandas as pd
import os
from datetime import datetime, timedelta
# get only the tweet text. no additional information
def getCSV(q):
	consumer_key = 'xe0AylJIY70ajsgiqaH9nhiN8'
	consumer_secret = 'ppSTBFemSNYFcd12AeWZ8qs7B3EcQVlBiZSBLsjzC3fVUctY1p'
	access_token = '1102516793275494400-fsRMutAx1xLtSiMAuhQCbtNYByp6Hz'
	access_token_secret = 'eJ2dD5GcCU5Fy4HTBwvNQJFyFOBKly3szvUrIEtkSRgNQ'

	auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
	auth.set_access_token(access_token, access_token_secret)
	api = tweepy.API(auth,wait_on_rate_limit=True)
	filename = "/home/nithin/Git/Cryptic/SentimentAnalysis/Twitter/"+q+"TwitterValid.csv"
	try:
		os.remove("/home/nithin/Git/Cryptic/SentimentAnalysis/Twitter/"+q+"TwitterValid.csv")
	except OSError:
		pass
	csvFile = open(filename, 'a')
	csvWriter = csv.writer(csvFile)
	csvWriter.writerow(["Tweet"])
	dict = {}
	most_retweets = []
	for tweet in tweepy.Cursor(api.search,q=q,
		                   lang="en", 
		                   until=datetime.strftime(datetime.now(),'%Y-%m-%d')).items(1000):
		temp = tweet.text
		temp = re.sub("\n"," ",temp)
		temp = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+','',temp)
		temp = re.sub(r'[^A-Za-z0-9]+', ' ', temp)
		csvWriter.writerow([temp])
		dict[tweet.retweet_count] = temp
	for i in sorted(dict, reverse = True)[:10]:
		most_retweets.append((i,dict[i]))
	#print(most_retweets)
	return most_retweets
	


# getCSV('Bitcoin')
