# import SentimentIntensityAnalyzer class
# from vaderSentiment.vaderSentiment module.
import pandas as pd
import re
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

# function to print sentiments
# of the sentence.


def sentiment_scores(sentence):

    # Create a SentimentIntensityAnalyzer object.
    sid_obj = SentimentIntensityAnalyzer()
    sentiment_dict = sid_obj.polarity_scores(sentence)
    if sentiment_dict['compound'] >= 0.05:
        return int(2)

    elif sentiment_dict['compound'] <= - 0.05:
        return int(0)

    else:
        return int(1)


def conversion(text):
    print("*****", text)
    text = str(text)
    text = text.lower()				# Convert to Lower
    text = text.strip().split()		# Convert to list
    if(text[0] == "rt"):			# Remove RT
        text = text[1:]
    text = ' '.join(text)
    return text


def RedditVader(coin):
    fields = ['Content']
    headers = fields + ['Label']
    labels = []
    df = pd.read_csv('/home/nithin/Git/Cryptic/SentimentAnalysis/Reddit/NewCSV/' +
                     coin + 'RedditValid.csv', skipinitialspace=True, usecols=fields)
    # print(df)
    # print(df["Content"])
    # print(type(df["Content"]))

    df["Content"] = df["Content"].map(conversion)
    # df.drop("[removed]",""," ", axis = 0, inplace = True)
    # df.drop("[removed]", axis = 0, inplace = True)
    # print(df)
    for row in df.iterrows():
        text = str(row[1])  # row[0] is the index. Do not use that.
        labels.append(sentiment_scores(text))

    df.insert(1, "Label", labels, allow_duplicates=True)
    df.to_csv('/home/nithin/Git/Cryptic/SentimentAnalysis/Reddit/NewTSV/' +
              coin+'RedditValid.tsv', sep='\t', columns=headers, index=False)
