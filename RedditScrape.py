#! /usr/bin/env python3
import praw
import csv
import pandas as pd
import datetime as dt
import os
from prawcore import NotFound

reddit = praw.Reddit(client_id='o3gxdBD030I0_A', \
                     client_secret='4nwjEfRCv8diJ6ukf9FaIn2oz1E', \
                     user_agent='Crypto Trading Bot', \
                     username='thanos10911694', \
                     password='Thanos8Sem')

def sub_exists(sub):
    exists = True
    try:
        reddit.subreddits.search_by_name(sub, exact=True)
    except NotFound:
        exists = False
    return exists
def getRedditContent(sub):
    if(not sub_exists(sub)):
        return 0
    else:
    	subreddit = reddit.subreddit(sub)
    	try:
    		os.remove("/home/nithin/Git/Cryptic/SentimentAnalysis/Reddit/NewCSV/"+sub+"RedditValid.csv")
    	except OSError:
    		pass
    	csvFile = open("/home/nithin/Git/Cryptic/SentimentAnalysis/Reddit/NewCSV/"+sub+"RedditValid.csv", 'a')
    	csvWriter = csv.writer(csvFile)
    	csvWriter.writerow(["Content"])
    	i = 0
    	for submission in reddit.subreddit(sub).top(limit = 1000):
    		if submission.is_self:
    			csvWriter.writerow([submission.selftext])
    			i+=1
    return 1