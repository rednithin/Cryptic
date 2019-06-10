# import SentimentIntensityAnalyzer class 
# from vaderSentiment.vaderSentiment module. 
import pandas as pd
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 

def sentiment_scores(sentence): 

	# Create a SentimentIntensityAnalyzer object. 
	sid_obj = SentimentIntensityAnalyzer() 

	# polarity_scores method of SentimentIntensityAnalyzer 
	# oject gives a sentiment dictionary. 
	# which contains pos, neg, neu, and compound scores. 
	sentiment_dict = sid_obj.polarity_scores(sentence) 
	
	# decide sentiment as positive, negative and neutral 
	if sentiment_dict['compound'] >= 0.05 : 
		return int(2)

	elif sentiment_dict['compound'] <= - 0.05 : 
		return int(0) 

	else : 
		return int(1)

def conversion(text):
	text = text.lower()		
	text = text.strip().split()		
	if(text[0] == "rt"):			
		text = text[1:]
	text = ' '.join(text)
	return text
 
def getSentiment(input_file,output_file,fields): 
	#Extract only the tweet content
	fields = fields
	headers = fields + ['Label']
	labels = []
	df = pd.read_csv(input_file, skipinitialspace=True, usecols=fields)
	for row in df.iterrows():
		tweet = str(row[1])		
		labels.append(sentiment_scores(tweet))
	for i in range(len(df.index)):
		df.at[i,str(fields[0])] = conversion(df.at[i,str(fields[0])])
	df.insert(1,"Label",labels,allow_duplicates = True)
	print(df.Label)
	df.to_csv(output_file, sep='\t',columns = headers, index = False)
	print(df.Label)
getSentiment('TwitterLitecoinTill7Apr.csv','TwitterLitecoinTill7Apr.tsv',['Tweet'])
