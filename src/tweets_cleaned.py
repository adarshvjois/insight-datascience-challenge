# example of program that calculates the number of tweets cleaned
import json
import sys

import logging
import re

logger = logging.getLogger('tweets_cleaned')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('run.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)


class CleanedTweet(object):
    tweets_with_unicode = 0
    whitespace = re.compile(r"\s+", re.MULTILINE)

    def clean_text(self, text):
        text = CleanedTweet.whitespace.sub(' ', text)
        counted = False
        cleaned_list = []
        for ch in text:
            if ord(ch) < 128:
                cleaned_list.append(ch)
            elif counted == False:
                CleanedTweet.tweets_with_unicode += 1
                counted = True

        return ''.join(cleaned_list)

    def __init__(self, text, timestamp):
        self.text = self.clean_text(text)
        self.timestamp = timestamp

    def __str__(self):
        return '{} (timestamp: {})'.format(self.text, self.timestamp)
        # return self.text + '(timestamp:' + self.timestamp + ')'


class JsonToText(object):

    def __init__(self, input_file, output_file):
        self.input_file = input_file
        self.output_file = output_file
        self.not_tweets = 0
        self.total_tweets = 0

    def clean_tweet(self, dct):
        if 'created_at' in dct and 'text' in dct:
            if dct['text'] == None:
                logger.debug('Text was none for tweet {}'.format(dct['id']))
                return None
            elif dct['created_at'] == None:
                logger.debug('No timestamp for tweet{}'.format(dct['id']))
                return None
            else:
                self.total_tweets += 1
                return CleanedTweet(dct['text'], dct['created_at'])
        else:
            self.not_tweets += 1
            return None

    def clean_tweets_from_input(self):
        with open(self.input_file, 'r') as tweets_file, open(self.output_file, 'w') as output:
            for line in tweets_file:
                stringified_json = json.loads(
                    line, object_hook=self.clean_tweet)
                if stringified_json != None:
                    output.write(str(stringified_json) + '\n')
            logger.info('Total tweets: {}'.format(self.total_tweets))
            logger.info(
                'Tweets with unicode: {}'.format(CleanedTweet.tweets_with_unicode))
            logger.info(
                'Objects other than tweets: {}'.format(self.not_tweets))


def get_inputs_from_cmd():
    if len(sys.argv) == 1:
        print "Use the '-h' option to learn to use this"
        sys.exit()
    elif sys.argv[1] == '-h' or sys.argv[1] == '--help':
        print "Use this program in the following way:"
        print "{} <input_file> <output_file>".format(sys.argv[0])
        sys.exit()
    elif len(sys.argv) >= 3:
        return sys.argv[1], sys.argv[2]
    else:
        print "Use the '-h' option to learn to use this"
        sys.exit()

if __name__ == '__main__':
    try:
        input_file, output_file = get_inputs_from_cmd()

        jsonToText = JsonToText(input_file, output_file)
        jsonToText.clean_tweets_from_input()

    except IOError as e:
        logger.error("Input file not found!")
