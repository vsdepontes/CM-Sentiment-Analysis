import pandas as pd
import got3 as got
from datetime import datetime, timedelta
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
import inquirer
from translate import Translator


class TwitterSentiments():
    def __init__(self):
        self.trans = Translator(to_lang = 'en')
        self.keyword = ''
        self.start_date = ''
        self.end_date = ''
        self.location = ''
        self.max_tweets = ''
        self.result_path = ''
    
    def search(self, keyword, start_date, end_date, location = None, max_tweets = 500, result_path = 'sentiment'):
        """
        Create and export sentiment data to CSV

        Dates should use the following format: 2020-05-18
        YYYY/MM/DD
        """
        self.keyword = str(keyword)
        self.start_date = str(start_date)
        self.end_date = str(end_date)
        self.location = str(location)
        self.max_tweets = max_tweets
        self.result_path = str(result_path)
        metaFile = open(self.result_path + ".txt", "w")
        metaFile.write("Keyword: " + self.keyword + "\n")
        metaFile.write("Location: " + self.location + "\n")
        metaFile.write("Max Tweets: " + str(self.max_tweets) + "\n")
        metaFile.close()
        file = open(self.result_path + ".csv", "w")
        file.write("Date,Positive,Negative\n")
        date_range_list = self._create_date_tuples()
        for day in date_range_list:
            day_tweets = self._get_tweets(day[0], day[1])
            day_sentiment = self._get_sentiment(day_tweets)
            file.write(f"{day[0]},{day_sentiment[0]},{day_sentiment[1]}")
            file.write("\n")
        file.close()    

    def _get_tweets(self, day_0, day_1):
        """
        Return tweets for an individual day, based on search criteria
        """
        tweetCriteria = (
            got.manager.TweetCriteria()
            .setQuerySearch(self.keyword)
            .setSince(day_0)
            .setUntil(day_1)
            .setWithin(self.location)
            .setTopTweets(True)
            .setMaxTweets(self.max_tweets)
        )
        return got.manager.TweetManager.getTweets(tweetCriteria)

    def _get_sentiment(self, tweets):
        """
        Return percentage pos / neg tweets for individual day
        """
        analyzer = SentimentIntensityAnalyzer()
        total_score = {"Positive": 0, "Negative": 0}
        for tweet in tweets:
            final_text = self.trans.translate(tweet.text)
            score = analyzer.polarity_scores(final_text)["compound"]
            if score >= 0.05:
                total_score["Positive"] += 1
            elif score <= -0.05:
                total_score["Negative"] += 1
        if sum(total_score.values()) > 0:
            return (
                round((total_score["Positive"] / sum(total_score.values())) * 100, 2),
                round((total_score["Negative"] / sum(total_score.values())) * 100, 2),
            )
        else:
            return(0, 0)
            
    def _date_range(self, date_1, date_2):
        """
        Return all the dates between two given dates
        """
        dt1 = datetime.strptime(date_1, "%Y-%m-%d")
        dt2 = datetime.strptime(date_2, "%Y-%m-%d")
        for n in range(int((dt2 - dt1).days) + 1):
            yield dt1 + timedelta(n)

    def _create_date_tuples(self):
        """
        Return list of tuples with start and end dates
        """
        from_date = [dt.strftime("%Y-%m-%d") for dt in self._date_range(self.start_date, self.end_date)]

        to_date = [
            dt.strftime("%Y-%m-%d")
            for dt in self._date_range(
                (datetime.strptime(self.start_date, "%Y-%m-%d") + timedelta(days=1)).strftime(
                    "%Y-%m-%d"
                ),
                (datetime.strptime(self.end_date, "%Y-%m-%d") + timedelta(days=1)).strftime(
                    "%Y-%m-%d"
                ),
            )
        ]
        return list(zip(from_date, to_date))