import pandas as pd
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer 

def sentiment_scores(sentence): 

    sid_obj = SentimentIntensityAnalyzer() 

    sentiment_dict = sid_obj.polarity_scores(sentence) 

    if sentiment_dict['compound'] >= 0.05 : 
        return int(2)

    elif sentiment_dict['compound'] <= - 0.05 : 
        return int(0) 

    else : 
        return int(1)

def conversion(text):
    
    text = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+','',text)
    text = re.sub('\n',' ',text)
    text = re.sub('\r',' ',text)
    text = re.sub("<p>",'',text)
    text = re.sub("</p>",'',text)
    text = re.sub("By CCN.com: ",'',text)
    text = re.sub("By CCN: ",'',text)
    text = text.lower()		
    text = text.strip().split()		
    if(text[0] == "rt"):			
        text = text[1:]
    text = ' '.join(text)
    return text
def NewsVader(coin):
	fields = ['Article']
	headers = fields + ['Label']
	labels = []
	df = pd.read_csv('/home/nithin/Git/Cryptic/SentimentAnalysis/News/CSV/'+coin+'NewsValid.csv', sep = '\t', skipinitialspace=True, usecols=fields)
	for row in df.iterrows():
	    tweet = str(row[1])		#row[0] is the index. Do not use that.
	    labels.append(sentiment_scores(tweet))
	for i in range(len(df.index)):
	    df.at[i,'Article'] = conversion(df.at[i,'Article'])
	df.insert(1,"Label",labels,allow_duplicates = True)
	#print(df)
	df.to_csv('/home/nithin/Git/Cryptic/SentimentAnalysis/News/TSV/'+coin+'NewsValid.tsv', sep='\t',columns = headers, index = False)
	#print(df.Label)

#NewsVader('Bitcoin')
