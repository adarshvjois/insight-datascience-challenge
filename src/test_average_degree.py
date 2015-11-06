'''
Created on Nov 4, 2015

@author: Adarsh
'''
import unittest
from datetime import datetime
from average_degree import htgraph, GoneIn60Seconds, Edge


class TestHtGraph(unittest.TestCase):

    def gen_ts(self, minutes, seconds, weekday='Sun', day='01', month='Jan', hour='00', year='1900'):
        timestr = '{} {} {} {}:{}:{} +0000 {}'.format(
            weekday, month, day, hour, minutes, seconds, year)
        return datetime.strptime(timestr, '%a %b %d %H:%M:%S +0000 %Y')

    def test_repeated_hts(self):
        G = htgraph()
        G.add_hts_to_graph(['#C', '#D', '#D', '#B'], self.gen_ts('2', '1'))
        self.assertEqual(2.0, G.average_degree())

    def test_multiple_evict_window(self):
        G = htgraph()
        G.add_hts_to_graph(['#C', '#D', '#B'], self.gen_ts('2', '1'))
        for i in range(2, 20):
            G.add_hts_to_graph(
                ['#A' + str(i), '#B' + str(i)], self.gen_ts('2', str(i)))
        G.add_hts_to_graph(['#D', '#C'], self.gen_ts('3', '2'))
        self.assertEqual(1.0, G.average_degree())

    def test_multiple_evict(self):
        G = htgraph()
        G.add_hts_to_graph(['#C', '#D', '#B'], self.gen_ts('2', '1'))
        G.add_hts_to_graph(['#A', '#B'], self.gen_ts('3', '2'))
        self.assertEqual(1.0, G.average_degree())

    def test_simple_evict(self):
        G = htgraph()
        G.add_hts_to_graph(['#A', '#B'], self.gen_ts('1', '0'))
        G.add_hts_to_graph(['#C', '#D', '#B'], self.gen_ts('2', '1'))
        self.assertEqual(2.0, G.average_degree())

    def test_simple_add(self):
        G = htgraph()
        G.add_hts_to_graph(['#A', '#B'], self.gen_ts('1', '0'))
        self.assertEqual(1.0, G.average_degree())

        self.assertSetEqual(set(['#A', '#B']), G.get_nodes())
        self.assertSetEqual(set([Edge(('#A', '#B'))]), G.get_edges())

        G.add_hts_to_graph(['#A', '#B', '#C'], self.gen_ts('1', '1'))
        self.assertEqual(2.0, G.average_degree())
        self.assertSetEqual(set(['#A', '#B', '#C']), G.get_nodes())
        self.assertSetEqual(
            set([Edge(('#A', '#B')), Edge(('#B', '#C')), Edge(('#C', '#A'))]),
            G.get_edges())


class TestGoneIn60Seconds(unittest.TestCase):

    @staticmethod
    def contains(l, obj):
        return obj in l

    def test_time_stamp_regex(self):
        tweet = 'lots of words here, that describe something surely' + \
            ' (timestamp: bingo!)'
        timestamps = GoneIn60Seconds.timestamp_regex.findall(tweet)
        self.assertEqual('bingo!', timestamps[0])

    def test_single_hashtag_regex(self):
        text = 'blah blah #boom'
        hashtags = GoneIn60Seconds.hashtag_regex.findall(text)
        self.assertEqual('#boom', hashtags[0])

    def test_hashtag_at_start(self):
        text = '#blah blah boom'
        hashtags = GoneIn60Seconds.hashtag_regex.findall(text)
        self.assertEqual('#blah', hashtags[0])

    def test_multiple_hashtag_regex(self):
        text = 'blah #blah #boom ... --- #time #maybe #it will miiss #this time'
        hashtags = GoneIn60Seconds.hashtag_regex.findall(text)
        self.assertEqual(True, TestGoneIn60Seconds.contains(hashtags, '#blah'))
        self.assertEqual(True, TestGoneIn60Seconds.contains(hashtags, '#boom'))
        self.assertEqual(
            True, TestGoneIn60Seconds.contains(hashtags, '#maybe'))
        self.assertEqual(True, TestGoneIn60Seconds.contains(hashtags, '#it'))
        self.assertEqual(True, TestGoneIn60Seconds.contains(hashtags, '#this'))
        self.assertEqual(True, TestGoneIn60Seconds.contains(hashtags, '#time'))

    def test_number_in_hashtag(self):
        text = '#1blah blah boom'
        hashtags = GoneIn60Seconds.hashtag_regex.findall(text)
        self.assertEqual('#1blah', hashtags[0])

    def test_many_hashtags_with_numbers(self):
        text = 'blah #blah #2boom ... --- #34maybe #i1t will miiss' + \
            ' #232818this #9time'
        hashtags = GoneIn60Seconds.hashtag_regex.findall(text)
        self.assertEqual(True, TestGoneIn60Seconds.contains(hashtags, '#blah'))
        self.assertEqual(
            True, TestGoneIn60Seconds.contains(hashtags, '#2boom'))
        self.assertEqual(
            True, TestGoneIn60Seconds.contains(hashtags, '#34maybe'))
        self.assertEqual(True, TestGoneIn60Seconds.contains(hashtags, '#i1t'))
        self.assertEqual(
            True, TestGoneIn60Seconds.contains(hashtags, '#232818this'))
        self.assertEqual(
            True, TestGoneIn60Seconds.contains(hashtags, '#9time'))

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
