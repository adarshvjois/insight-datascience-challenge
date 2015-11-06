'''
Created on Nov 4, 2015

@author: Adarsh
'''
import unittest

from tweets_cleaned import CleanedTweet


class CleanedTweetTest(unittest.TestCase):

    def test_remove_newline_with_unicode(self):
        test_tweet = ''.join([u'\uab10'] * 100) + 'some\ntext'
        ct = CleanedTweet(test_tweet, 'xyz')
        self.assertEqual(str(ct), 'some text (timestamp: xyz)')
    
    def test_remove_newline_without_unicode(self):
        test_tweet = 'some\ntext'
        ct = CleanedTweet(test_tweet, 'xyz')
        self.assertEqual(str(ct), 'some text (timestamp: xyz)')

    def test_lots_of_unicode_starts(self):
        test_tweet = ''.join([u'\uab10'] * 100) + 'some text'
        ct = CleanedTweet(test_tweet, 'xyz')
        self.assertEqual(str(ct), 'some text (timestamp: xyz)')

    def test_lots_of_unicode_end(self):
        test_tweet = 'some text' + ''.join([u'\uab10'] * 100)
        ct = CleanedTweet(test_tweet, 'xyz')
        self.assertEqual(str(ct), 'some text (timestamp: xyz)')

    def test_lots_of_unicode_left_and_right(self):
        test_tweet = ''.join([u'\uab10'] * 20) + \
            ' some text ' + ''.join([u'\uaa00'] * 20)
        ct = CleanedTweet(test_tweet, 'xyz')
        self.assertEqual(str(ct), ' some text  (timestamp: xyz)')

    def test_unicode_start(self):
        test_tweet = u'\u1234' + 'some text'
        ct = CleanedTweet(test_tweet, 'xyz')
        self.assertEqual(str(ct), 'some text (timestamp: xyz)')

    def test_unicode_end(self):
        test_tweet = 'some text' + u'\u1234'
        ct = CleanedTweet(test_tweet, 'xyz')
        self.assertEqual(str(ct), 'some text (timestamp: xyz)')

    def test_unicode_in_between(self):
        test_tweet = 'some text' + u'\u1234' + ' more text'
        ct = CleanedTweet(test_tweet, 'xyz')
        self.assertEqual(str(ct), 'some text more text (timestamp: xyz)')


if __name__ == '__main__':
    unittest.main()
