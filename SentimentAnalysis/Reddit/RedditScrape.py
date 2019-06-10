'''
#! /usr/bin/env python3
import praw
import pandas as pd
import datetime as dt

def getPushshiftData(query, after, before, sub):
    url = 'https://api.pushshift.io/reddit/search/submission/?title='+str(query)+'&size=1000&after='+str(after)+'&before='+str(before)+'&subreddit='+str(sub)
    print(url)
    r = requests.get(url)	#data obtained in json format
    pprint(r)
    
    print("================================R.TEXT :==================================")
    pprint(r.text)
    data = json.loads(r.text)	#converts the obtained data to a python dictionary
    return data['data']
    
reddit = praw.Reddit(client_id='o3gxdBD030I0_A', \
                     client_secret='4nwjEfRCv8diJ6ukf9FaIn2oz1E', \
                     user_agent='Crypto Trading Bot', \
                     username='thanos10911694', \
                     password='Thanos8Sem')

#subreddit = reddit.subreddit('Bitcoin')
i=0

for submission in reddit.subreddit('Bitcoin').top('all'):
    print(submission.created_utc)
    i+=1
    if(i==1500):
    	break
print(i)
'''
#! /usr/bin/env python3
import praw
import pandas as pd
import datetime
import time
import requests
import pprint
import json
import csv

import re

def getPushshiftData(query, after, before, sub):
    url = 'https://api.pushshift.io/reddit/search/submission/?title='+str(query)+'&size=1000&after='+str(after)+'&before='+str(before)+'&subreddit='+str(sub)
    print(url)
    r = requests.get(url)	#data obtained in json format
    #pprint(r)
    
    print("================================R.TEXT :==================================")
    #pprint(r.text)
    data = json.loads(r.text)	#converts the obtained data to a python dictionary
    #print(data.keys())
    print(type(data))
    for key in data:
        print(key)
    return data['data']

def collectSubData(subm,subStats):


    subData = list() #list to store data points
    # title = subm['title']
    # url = subm['url']
    # try:
    #     flair = subm['link_flair_text']
    # except KeyError:
    #     flair = "NaN"    
    # author = subm['author']
    sub_id = subm['id']
    # print(subm.keys())
    # score = subm['score']
    # created = datetime.datetime.fromtimestamp(subm['created_utc']) #1520561700.0
    # numComms = subm['num_comments']
    # permalink = subm['permalink']
    content = subm['selftext']
    
    subData.append((content))
    subStats[sub_id] = subData 

def updateSubs_file(subStats):
    upload_count = 0
    location = "/home/nithin/Git/Cryptic/SentimentAnalysis/Reddit/"
    #print("input filename of submission file, please add .csv")
    #filename = input()
    filename = "LitecoinReddit1Month.csv"
    file = location + filename
    with open(file, 'w', newline='', encoding='utf-8') as file: 
        a = csv.writer(file, delimiter=',')
        headers = ["Content"]
        a.writerow(headers)
        for sub in subStats:
            a.writerow(subStats[sub])
            upload_count+=1
            
        print(str(upload_count) + " submissions have been uploaded")

#updateSubs_file()

def main():
    subReddit='Litecoin'
    #before and after dates
    #---before = "1538352000" #October 1st
    #before = str(int(time.time()))  #Now

    before = "1556625600"   # Apr 30 2019 For Altcoin
    # before = "1553731200" # Mar 28th 2019
    # after = "1550188800"    # Feb 15th 2019
    after = "1546300800"    # Jan 1 2019 For Altcoin

    #after = "1552262400"#11th March 2019        #"1334426439"   #14th April 2012 
    query = ""
    subCount = 0
    subStats = {}
    data = getPushshiftData(query, after, before, subReddit)
    print("in main")
    print(len(data))
    # Will run until all posts have been gathered 
    # from the 'after' date up until before date
    while len(data) > 0:
    	print("in while")
    	for submission in data:
        	collectSubData(submission,subStats)
        	subCount+=1
    	# Calls getPushshiftData() with the created date of the last submission
    	# print(len(data))
    	print(str(datetime.datetime.fromtimestamp(data[-1]['created_utc'])))
    	after = data[-1]['created_utc']
    	data = getPushshiftData(query, after, before, subReddit)
    
    print(len(data))
    print(subCount)
    updateSubs_file(subStats)


if __name__ == "__main__":
    main()


'''
reddit = praw.Reddit(client_id='o3gxdBD030I0_A', \
                     client_secret='4nwjEfRCv8diJ6ukf9FaIn2oz1E', \
                     user_agent='Crypto Trading Bot', \
                     username='thanos10911694', \
                     password='Thanos8Sem')

#subreddit = reddit.subreddit('Bitcoin')
i=0

for submission in reddit.subreddit('Bitcoin').top('all'):
    print(submission.created_utc)
    i+=1
    if(i==1500):
    	break
print(i)
'''
