import tweepy
import csv
import re
import pandas as pd
# get only the tweet text. no additional information
def getTweets(q,filename,from_date):
	csvFile = open(filename, 'a')
	csvWriter = csv.writer(csvFile)
	csvWriter.writerow("Tweet\n")
	for tweet in tweepy.Cursor(api.search,q=q,
		                   lang="en", 
		                   since=from_date).items():
		temp = tweet.text
		temp = re.sub("\n"," ",temp)
		temp = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+','',temp)
		temp = re.sub(r'[^A-Za-z0-9]+', ' ', temp)
		csvWriter.writerow([temp])

# get tweet text and number of retweets
def getTweetsRetweets(q,filename,from_date):
	csvFile = open(filename, 'a')
	csvWriter = csv.writer(csvFile)
	csvWriter.writerow("Tweet\tRetweets\n")
	for tweet in tweepy.Cursor(api.search,q=q,
		                   lang="en", 
		                   since=from_date).items():
		temp = tweet.text
		temp = re.sub("\n"," ",temp)
		temp = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+','',temp)
		temp = re.sub(r'[^A-Za-z0-9]+', ' ', temp)
		csvWriter.writerow([temp,tweet.retweet_count])

consumer_key = 'xe0AylJIY70ajsgiqaH9nhiN8'
consumer_secret = 'ppSTBFemSNYFcd12AeWZ8qs7B3EcQVlBiZSBLsjzC3fVUctY1p'
access_token = '1102516793275494400-fsRMutAx1xLtSiMAuhQCbtNYByp6Hz'
access_token_secret = 'eJ2dD5GcCU5Fy4HTBwvNQJFyFOBKly3szvUrIEtkSRgNQ'

auth = tweepy.OAuthHandler(consumer_key, consumer_secret)
auth.set_access_token(access_token, access_token_secret)
api = tweepy.API(auth,wait_on_rate_limit=True)

getTweets("Bitcoin","TwitterBitcoin1.csv","2019-03-07")
