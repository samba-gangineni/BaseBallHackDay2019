import json
import re
import tweepy
import datetime
import pandas as pd
r = re.compile('^\w+$')

class TwitterScrapper(object):

    def __init__(self):
        # configuration keys
        self.keys = json.load(open('config.json', 'r'))
                
        # Twitter API Authentication
        self.auth = tweepy.OAuthHandler(self.keys['consumer_key'], self.keys['consumer_secret'])
        self.auth.set_access_token(self.keys['access_token'], self.keys['access_token_secret'])
        self.api = tweepy.API(self.auth, wait_on_rate_limit=True)

        # Twitter Search API Parameters
        self.lang = 'en'
        self.geocode = ''
        self.until = datetime.datetime.today().strftime('%Y-%m-%d')
        self.since = datetime.datetime.today() - datetime.timedelta(days=10)  # Twitter Standard API has limit of 7-10 days
        self.since = self.since.strftime('%Y-%m-%d')

    def refine(self, tweet_texts: list):
        for i in range(len(tweet_texts)):
            if tweet_texts[i]:
                not_required = ['"', '"', "'", '.', '&', ',', '‘', '’', '”', '“']
                for nr in not_required:
                    tweet_texts[i] = tweet_texts[i].replace(nr, '')

                tweet_texts[i] = ' '.join(filter(lambda x: 'https' not in x, tweet_texts[i].split()))
                tweet_texts[i] = ' '.join(filter(lambda x: 'http' not in x, tweet_texts[i].split()))
                tweet_texts[i] = ' '.join(filter(lambda x: '@' not in x, tweet_texts[i].split()))
                for word in filter(lambda x: x[0] == '#', tweet_texts[i].split()):
                    tweet_texts[i] = tweet_texts[i].replace(word,
                                                            re.sub(r'([a-z](?=[A-Z])|[A-Z](?=[A-Z][a-z]))', r'\1 ', word))

                for word in tweet_texts[i].split():
                    if not re.match(r, word):
                        tweet_texts[i] = tweet_texts[i].replace(word, '')

                tweet_texts[i] = tweet_texts[i].lower()
        return tweet_texts


    def scrapper(self, details:list):
        enlistedtweets = []
        texts = []
       
        # Scrapping and storing tweets of a handle or hashtag
        for tag in details:
            print("Tag: ", tag)
            data_point = tag

            # based upon search query on twitter handle or hashtag
            query = data_point
            if self.geocode:
                result_obj = tweepy.Cursor(self.api.search, q=query, since=self.since, until=self.until, geocode=geocode, tweet_mode='extended')
            else:
                result_obj = tweepy.Cursor(self.api.search, q=query, since=self.since, until=self.until, tweet_mode='extended')
            for tweet in result_obj.items():
                if len(texts) > 100:
                    break
                print(tweet._json['id'])
                if tweet._json['id'] not in enlistedtweets:
                    enlistedtweets.append(tweet._json['id'])
                    if 'retweeted_status' in tweet._json:
                        if tweet._json['retweeted_status'].get('id') not in enlistedtweets:
                            texts.append(tweet._json['retweeted_status'].get('full_text'))
                            enlistedtweets.append(tweet._json['retweeted_status'].get('id'))
                    else:
                        if tweet._json.get('id') not in enlistedtweets:
                            texts.append(tweet._json['full_text'])
                if 'in_reply_to_status_id' in tweet._json:
                    x = tweet._json['in_reply_to_status_id']
                    while x is not None:
                        if x not in enlistedtweets:
                            try:
                                tweet_value = self.api.get_status(id=x, tweet_mode='extended')
                                enlistedtweets.append(tweet_value._json['in_reply_to_status_id'])
                                if 'retweeted_status' in tweet_value._json:
                                    if tweet_value._json['retweeted_status'].get('id') not in enlistedtweets:
                                        texts.append(tweet_value._json['retweeted_status'].get('full_text'))
                                        enlistedtweets.append(tweet_value._json['retweeted_status'].get('id'))
                                else:
                                    if tweet_value._json.get('id') not in enlistedtweets:
                                        texts.append(tweet_value._json['full_text'])
                                x = tweet_value._json['in_reply_to_status_id']
                            except tweepy.TweepError:
                                break
                        else:
                            break 
                

            # based upon users timeline (limit 3200 tweets)
            try:
                if '@' in data_point:
                    alltweets = []
                    new_tweets = self.api.user_timeline(screen_name=data_point.replace('@', ''), count=200, tweet_mode='extended')
                    alltweets.extend(new_tweets)
                    oldest = alltweets[-1].id - 1
                    for tweet in new_tweets:
                        if len(texts) > 100:
                            break
                        if tweet._json['id'] not in enlistedtweets:
                            enlistedtweets.append(tweet._json['id'])
                            if 'retweeted_status' in tweet._json:
                                if tweet._json['retweeted_status'].get('id') not in enlistedtweets:
                                    texts.append(tweet._json['retweeted_status'].get('full_text'))
                                    enlistedtweets.append(tweet._json['retweeted_status'].get('id'))
                            else:
                                if tweet._json.get('id') not in enlistedtweets:
                                    texts.append(tweet._json['full_text'])
                        if 'in_reply_to_status_id' in tweet._json:
                            x = tweet._json['in_reply_to_status_id']
                            while x is not None:
                                if x not in enlistedtweets:
                                    try:
                                        tweet_value = self.api.get_status(id=x, tweet_mode='extended')
                                        enlistedtweets.append(tweet_value._json['in_reply_to_status_id'])
                                        if 'retweeted_status' in tweet_value._json:
                                            if tweet_value._json['retweeted_status'].get('id') not in enlistedtweets:
                                                texts.append(tweet_value._json['retweeted_status'].get('full_text'))
                                                enlistedtweets.append(tweet_value._json['retweeted_status'].get('id'))
                                        else:
                                            if tweet_value._json.get('id') not in enlistedtweets:
                                                texts.append(tweet_value._json['full_text'])
                                        x = tweet_value._json['in_reply_to_status_id']
                                    except tweepy.TweepError:
                                        break
                                else:
                                    break         
                    while len(new_tweets) > 0:
                        new_tweets = self.api.user_timeline(screen_name=data_point.replace('@', ''), count=200, max_id=oldest,
                                                    tweet_mode='extended')
                        for tweet in new_tweets:
                            if len(texts) > 100:
                                break
                            if tweet._json['id'] not in enlistedtweets:
                                enlistedtweets.append(tweet._json['id'])
                                if 'retweeted_status' in tweet._json:
                                    if tweet._json['retweeted_status'].get('id') not in enlistedtweets:
                                        texts.append(tweet._json['retweeted_status'].get('full_text'))
                                        enlistedtweets.append(tweet._json['retweeted_status'].get('id'))
                                else:
                                    if tweet._json.get('id') not in enlistedtweets:
                                        texts.append(tweet._json['full_text'])
                            if 'in_reply_to_status_id' in tweet._json:
                                x = tweet._json['in_reply_to_status_id']
                                while x is not None:
                                    if x not in enlistedtweets:
                                        try:
                                            tweet_value = api.get_status(id=x, tweet_mode='extended')
                                            enlistedtweets.append(tweet_value._json['in_reply_to_status_id'])
                                            if 'retweeted_status' in tweet_value._json:
                                                if tweet_value._json['retweeted_status'].get('id') not in enlistedtweets:
                                                    texts.append(tweet_value._json['retweeted_status'].get('full_text'))
                                                    enlistedtweets.append(tweet_value._json['retweeted_status'].get('id'))
                                            else:
                                                if tweet_value._json.get('id') not in enlistedtweets:
                                                    texts.append(tweet_value._json['full_text'])
                                            x = tweet_value._json['in_reply_to_status_id']
                                        except tweepy.TweepError:
                                            break
                                    else:
                                        break         
                        alltweets.extend(new_tweets)
                        oldest = alltweets[-1].id - 1
            except:
                pass

        return texts

    def preprocessing(self, tag_name, texts):
        # Scrapping and storing tweets of each representative
        texts = self.refine(texts)
        texts = [text for text in texts if text]
        df = pd.DataFrame(texts, columns=["text"])
        csv_name = tag_name + '.csv'
        df.to_csv(csv_name, index=False)
        return texts

    def main(self):
        print("Start")
        for team in ['Athletics','Diamondbacks','Pirates''Nationals','Angels','Mariners','Orioles','RedSox']:
            inp = ['#'+team,'@'+team] 
            tests = self.scrapper(inp)
            tests = self.preprocessing(team,tests)
            print("Scrapper done!")

if __name__ == "__main__":
    import time
    start_time = time.time()

    obj = TwitterScrapper()
    obj.main()

    print("--- %s seconds ---" % (time.time() - start_time))
