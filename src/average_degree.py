# example of program that calculates the average degree of hashtags
import sys
import re
from datetime import datetime
from datetime import timedelta
import itertools
import logging
from collections import OrderedDict
from _abcoll import Iterable
# import matplotlib.pyplot as plt
# import networkx as nx

logger = logging.getLogger('tweets_cleaned')
logger.setLevel(logging.DEBUG)

fh = logging.FileHandler('run2.log')
fh.setLevel(logging.DEBUG)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)

formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
fh.setFormatter(formatter)
ch.setFormatter(formatter)

logger.addHandler(fh)
logger.addHandler(ch)

# simplistic untested wrapper for a dict
# that always defaults to zero when an item
# is not found


class OrderedZeroDict(OrderedDict):

    def __getitem__(self, key):
        try:
            return OrderedDict.__getitem__(self, key)
        except KeyError:
            return 0

# a tuple that two way equal.
# > Edge((2,1)) == Edge((1, 2))
# True


class Edge(tuple):

    def __new__(self, edge_tup):
        return tuple.__new__(self, edge_tup)

    def __hash__(self):
        return hash(self[0]) + hash(self[1])

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        elif self[0] in other and self[1] in other:
            return True
        else:
            return False


class htgraph(object):

    def __init__(self, td=timedelta(seconds=60)):
        # Since tweets are expected to arrive in order,
        # the tweets we see first are going to be the first to get
        # pruned.
        self.__live_edges = OrderedZeroDict()
        self.td = td

    def get_edges(self):
        # makes set of edges immutable
        return frozenset(self.__live_edges.keys())

    def get_nodes(self):
        edges = self.__live_edges.keys()
        # flattens this and makes in immutable
        return frozenset(list(sum(edges, ())))

    def average_degree(self):
        edge_count = len(self.__live_edges)
        node_count = len(self.get_nodes())
        if node_count > 0:
            return 2.0 * float(edge_count) / float(node_count)
        else:  # sweeping this under the rug
            return 0.0

    def __prune_edge(self, edge):
        logger.info('Deleted {}'.format(edge))
        del self.__live_edges[edge]

    def maintain_edges(self, current_timestamp):
        for edge in self.__live_edges:
            if current_timestamp - self.__live_edges[edge] > self.td:
                logger.debug('Pruning {} ..'.format(edge))
                self.__prune_edge(edge)

#     def draw_graph(self):
#         # https://www.udacity.com/wiki/creating-network-graphs-with-python
#         nodes = self.get_nodes()
#         G = nx.Graph()
#         for node in nodes:
#             G.add_node(node)
#         edges = self.get_edges()
#         for edge in edges:
#             G.add_edge(edge[0], edge[1])
#         pos = nx.shell_layout(G)
#         nx.draw(G, pos)
#         plt.savefig(
#             '../my-images/htag_degree' + str(self.average_degree()) + '.png')

    def add_hts_to_graph(self, htlist, timestamp):
        if len(htlist) > 1:
            ht_edges = itertools.combinations(set(htlist), 2)

            incoming_edges = [(Edge(edge), timestamp)
                              for edge in ht_edges]

            # ensures that edges have only the latest timestamp
            # associated with them.
            self.__live_edges.update(dict(incoming_edges))
            logger.debug('Updated {}'.format(incoming_edges))

            current_timestamp = timestamp
            logger.debug(' Current timestamp {}'.format(str(timestamp)))
            self.maintain_edges(current_timestamp)

        else:
            logger.debug(' Current timestamp '.format(str(timestamp)))
            current_timestamp = timestamp
            self.maintain_edges(current_timestamp)


class GoneIn60Seconds(object):
    '''
    Parses the input tweets file and generates rolling average
    degree per tweet taken as input.
    '''

    hashtag_regex = re.compile(r'(#\d*\w+)')
    timestamp_regex = re.compile(r'\(timestamp: (.+)\)')

    def __init__(self):
        self.htgraph = htgraph()
        self.td = timedelta(seconds=60)

    def process_input(self, input_file, output_file):
        if not isinstance(input_file, Iterable):
            raise ValueError('First param is not Iterable')
        if not isinstance(output_file, file):
            raise ValueError('Second param is not a file')
        tweet_number = 0
        for tweet in input_file:
            tweet_number += 1

            hashtag_list = GoneIn60Seconds.hashtag_regex.findall(
                tweet.lower())
            timestamp_str = GoneIn60Seconds.timestamp_regex.findall(tweet)
            timestamp = datetime.strptime(
                timestamp_str[-1], '%a %b %d %H:%M:%S +0000 %Y')

            if len(hashtag_list) > 2:
                logger.info(', '.join(hashtag_list) + ' ' + str(timestamp))

                self.htgraph.add_hts_to_graph(hashtag_list, timestamp)

                logger.info(
                    'ROLLING {}'.format(str(self.htgraph.average_degree())))
                output_file.write(str(self.htgraph.average_degree()) + '\n')
#               self.htgraph.draw_graph()
#           if tweet_number % 500 == 0:
#                logger.info(
#                    "Drawing a graph for the {}th tweet".format(tweet_number))
#                self.htgraph.draw_graph()
            else:
                self.htgraph.maintain_edges(timestamp)


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
    input_file, output_file = get_inputs_from_cmd()
    win = GoneIn60Seconds()
    win.process_input(open(input_file, 'r'), open(output_file, 'w'))
