import pandas as pd
from plotly.offline import plot,iplot
import plotly.figure_factory as ff
import os
import json
import requests
from flask import (
	Flask, render_template, request, session, flash, url_for, redirect, make_response
	)
from stanfordcorenlp import StanfordCoreNLP
from nltk import word_tokenize
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer
from string import punctuation
from gensim.corpora import HashDictionary
from gensim.models import TfidfModel
from wordcloud import WordCloud
from textblob import TextBlob
import pandas as pd


# Flask app connection
app = Flask(__name__)
app.secret_key = 'BaseBall'
app.config['SESSION_TYPE'] = 'filesystem'


# nlp = StanfordCoreNLP(r'C:\Users\harsh\Downloads\stanford-corenlp-full-2018-10-05')
properties = {
    'annotators': 'sentiment',
    'outputFormat': 'json',
    'timeout': 10000,
}
sentimentVal = {0: 'Strong Negative', 1: 'Negative', 2: 'Neutral', 3: 'Positive', 4: 'Strong Positive'}
stop_words = stopwords.words('english') + list(punctuation)


def create_word_cloud( freq: dict, filename: str):
    # Initialize the word cloud
    wc = WordCloud(
        background_color="white",
        max_words=2000,
        width=1024,
        height=720,
        stopwords=stop_words
    )
    # Generate the cloud
    wc.generate_from_frequencies(freq)
    # Save the could to a file
    wc.to_file('static/img/'+filename + ".png")


def tokenize( text):
    words = word_tokenize(text)
    words = [w for w in words if w not in stop_words and not w.isdigit()]

    # Lemmatization
    wnl = WordNetLemmatizer()
    words = [wnl.lemmatize(w) for w in words]
    return words


def apply_tfidf( reviews_text: list):
    dictionary = HashDictionary()
    review_tokens = []
    for result in reviews_text:
        # Tokenize the reviews
        review_tokens.append(tokenize(result))

    # Build the dictionary
    dictionary.add_documents(review_tokens)
    # Convert to vector corpus
    vectors = [dictionary.doc2bow(token) for token in review_tokens]
    # Build TF-IDF model
    tfidf = TfidfModel(vectors)
    # Get TF-IDF weights
    weights = tfidf[vectors]
    # Get terms from the dictionary and pair with weights
    freq = dict()
    for doc in weights:
        for pair in doc:
            list_of_words = list(dictionary[pair[0]])
            for word in list_of_words:
                if word in freq:
                    freq[word] += pair[1]
                else:
                    freq[word] = pair[1]
    return freq


def calculate_sentiment(review_text: str):
    res_senti = 0
    res = nlp.annotate(review_text, properties=properties)
    try:
        if res:
            if isinstance(res, str):
                res = json.loads(res)
            for s in res["sentences"]:
                res_senti += int(s["sentimentValue"])
            return int(res_senti / len(res['sentences']))
    except Exception as e:
        print(e)
        print(res)
        return None


def sentiment_analyse(reviews: list):
    neg_sentiment, pos_sentiment = [], []
    for review_text in reviews:
        try:
            if calculate_sentiment(review_text):
                if calculate_sentiment(review_text) < 2:
                    neg_sentiment.append(review_text)
                elif calculate_sentiment(review_text) > 2:
                    pos_sentiment.append(review_text)
        except Exception:
            # Due to NoneType return by calculate_sentiment
            continue
    return neg_sentiment, pos_sentiment

def textBlob(reviews):
    neg_sentiment, pos_sentiment = [], []
    for review_text in reviews:
        blob = TextBlob(review_text)
        if blob.sentiment[0] < 0:
            neg_sentiment.append(review_text)
        elif blob.sentiment[0] > 0:
            pos_sentiment.append(review_text)
    return neg_sentiment, pos_sentiment

@app.route('/')
@app.route('/api/v1/')
def home():
	schedule = pd.read_csv('results_2018.csv')
	schedule.sort_values('Date')
	teams=[]
	match={}
	details={}
	for i in range(5):
		if schedule.iloc[i]['Home'] not in ['Athletics','Angels','Mariners','Orioles','RedSox'] or schedule.iloc[i]['Away'] not in ['Athletics','Angels','Mariners','Orioles','RedSox']:
			continue  
		if schedule.iloc[i]['Home'] not in teams:
			teams.append(schedule.iloc[i]['Home'].replace(' ',''))
		if schedule.iloc[i]['Away'] not in teams:
			teams.append(schedule.iloc[i]['Away'].replace(' ',''))
		print(schedule.iloc[i]['Home'])
		print(schedule.iloc[i]['Away'])
		match[(schedule.iloc[i]['Home'],schedule.iloc[i]['Away'])]=[]
	print("Teams:",teams)
	for team in teams:
		try:
			tests = pd.read_csv(team+'.csv')['text'].to_list()
			neg_sentis, pos_sentis = textBlob(tests)
			print("Negative Sentiment: {} ".format(len(neg_sentis)/(len(neg_sentis)+len(pos_sentis))))
			print("Positive Sentiment: {} ".format(len(pos_sentis)/(len(neg_sentis)+len(pos_sentis))))
			neg_freq = apply_tfidf(neg_sentis)
			pos_freq = apply_tfidf(pos_sentis)
			create_word_cloud(neg_freq, team+'_neq')
			create_word_cloud(pos_freq, team+'_pos')
			details[team]=[len(neg_sentis)/(len(neg_sentis)+len(pos_sentis)),len(pos_sentis)/(len(neg_sentis)+len(pos_sentis)), team+'_neq.png', team+'_pos.png']
		except:
			pass
	for i in range(5):
		if schedule.iloc[i]['Home'] not in ['Athletics','Angels','Mariners','Orioles','RedSox'] or schedule.iloc[i]['Away'] not in ['Athletics','Angels','Mariners','Orioles','RedSox']:
			continue  
		match[(schedule.iloc[i]['Home'],schedule.iloc[i]['Away'])].append({
				'Away': schedule.iloc[i]['Away'],
				'Home': schedule.iloc[i]['Home'],
				'Away neg score':details[schedule.iloc[i]['Away']][0],
				'Away pos score':details[schedule.iloc[i]['Away']][1],
				'Home neg score':details[schedule.iloc[i]['Home']][0],
				'Home pos score':details[schedule.iloc[i]['Home']][1],
				'away_link_nscore':details[schedule.iloc[i]['Away']][2],
				'away_link_pscore':details[schedule.iloc[i]['Away']][3],
				'home_link_nscore':details[schedule.iloc[i]['Home']][2],
				'home_link_pscore': details[schedule.iloc[i]['Home']][3],
				'Result': schedule.iloc[i]['Results']
			})
	return render_template('index.html',match=match)





if __name__ == '__main__':
	app.run(host='0.0.0.0',port=8080,debug=True)
