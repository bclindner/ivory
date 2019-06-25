from core import Rule, Report
import xml.etree.ElementTree as ET
import re
from functools import reduce

striptags = re.compile(r'(<!--.*?-->|<[^>]*>)')
def tokenize(data: str):
    # remove HTML tags
    # data = ET.tostring(ET.fromstring(data), encoding='utf8', method='text').decode('utf-8')
    data = re.sub(striptags, '', data)
    # remove punctuation, lowercase, split by space
    data = re.sub('[,.\!\'\"\\\/\`\(\)\[\]\{\}\-\_\+\=\:\;]', ' ', data).casefold().split()
    # make unique by converting to set
    return set(data)
    

class NaiveBayesFilter:
    """
        A Naive Bayes spam filter.

        Implemented directly from formulae in this Wikipedia document:
        https://en.wikipedia.org/wiki/Naive_Bayes_spam_filtering

        This spam filter can be trained by passing messages to its train()
        method, and tested from the tested data using the test() method. See
        individual function documentations for details.

        To save the dataset, simply take the "data" property of the class (a
        dict), serialize it how you will (i.e. with json.dump()), and save it
        to a file. To load the dataset, load the data from that file into a
        dict (i.e. with json.load()) and pass it in as a parameter when
        creating the class.
    """
    def __init__(self, data={}):
        self.data = data
    def train(self, message, spam):
        """
        Train the current filter model based on a new message.

        Arguments:
        message (str) -- The message to train from. The filter will attempt
        to sanitize and tokenize it (though it won't hurt to do some of that
        yourself).
        spam (bool) -- Whether or not the message is spam.
        """
        for token in tokenize(message):
            if token in self.data:
                self.data[token]['t'] += 1
            else:
                self.data[token] = {
                    "t": 1,
                    "s": 0,
                    "h": 0
                }
            self.data[token]['s'] += 1 if spam else 0
            self.data[token]['h'] += 1 if not spam else 0
    def test(self, message):
        """
        Test a message against the current model.

        The algorithm from this is ripped directly from Wikipedia:
        https://en.wikipedia.org/wiki/Naive_Bayes_spam_filtering#The_spamliness_of_a_word

        Arguments:
        message (str) -- The message to test.

        Returns:
        float -- The probability that the message is spam.
        """
        spam_probabilities = []
        for token in tokenize(message):
            # discard all unknown tokens
            if token in self.data:
                tokendata = self.data[token]
                spamprob = tokendata['s'] / tokendata['t']
                hamprob = tokendata['h'] / tokendata['t']
                spamminess = spamprob / (spamprob + hamprob)
                if spamminess != 0.0:
                    spam_probabilities.append(spamminess)
        spam_complements = [1 - probability for probability in spam_probabilities]
        # https://stackoverflow.com/questions/2104782/returning-the-product-of-a-list
        probability_product = reduce(lambda x, y: x*y, spam_probabilities, 1)
        complement_product = reduce(lambda x, y: x*y, spam_complements, 1)
        overall_spamminess = probability_product / (probability_product + complement_product)
        return overall_spamminess

class BayesRule(Rule):
    def __init__(self, config):
        Rule.__init__(self, config)
    def test(self, report: Report):
        pass