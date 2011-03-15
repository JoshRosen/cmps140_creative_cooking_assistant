import nltk
from nltk.corpus import wordnet
import cPickle
import logging
import os

def stem_words(words, stemmer=nltk.PorterStemmer(), lcase=True):
    """
    returns a stemmed list of words
    """
    word_stems = []
    for word in words:
        if lcase:
            word = stemmer.stem(word).lower()
        else:
            word = stemmer.stem(word)
        word_stems.append(word)
    return  word_stems


def min_synset_distance_in_sentence(synset_strings, tokenized_string):
    """
    Finds the closests distance of synsets from synset_strings compared to
    any token in tokenized_string. A tuple of ((token, index), distance) is
    returned if a result is found, otherwise None is returned.
    """
    minDistanceSet = None
    for synset_string in synset_strings:
        synset = wordnet.synset(synset_string)
        for i, token in enumerate(tokenized_string):
            token_synsets = wordnet.synsets(token)
            for token_synset in token_synsets:
                distance = synset.shortest_path_distance(token_synset)
                if minDistanceSet == None or (distance != None and 
                   distance < minDistanceSet[1]):
                    minDistanceSet = ((token, i), distance)
    return minDistanceSet


def combine_backoff_taggers( taggers, traningData ):
    """
    returns an initialized tagger combined from a list of backoff taggers
    """
    combined_tagger = taggers.pop()
    for tagger in taggers:
        combined_tagger = tagger(traningData, backoff=combined_tagger)
    return combined_tagger



def _load_combined_taggers():
    """
    Train and combine a series of POS taggers, but use a pickled tagger if it's
    available.  This avoids the expensive training process when reloading the
    application.
    """
    filename = os.path.join(os.path.dirname(__file__), 'combined_taggers.pkl')
    try:
        with open(filename, 'rb') as pickle_file:
            combined_taggers = cPickle.load(pickle_file)
        logging.info("Loaded combined tagger from %s" % filename)
    except IOError:
        logging.warn("Couldn't load tagger from %s, regenerating." % filename)
        taggers_to_combine = [
            nltk.TrigramTagger,
            nltk.BigramTagger,
            nltk.DefaultTagger('NN'),
        ]
        combined_taggers = combine_backoff_taggers(taggers_to_combine,
            nltk.corpus.nps_chat.tagged_posts())
        with open(filename, 'wb') as pickle_file:
            cPickle.dump(combined_taggers, pickle_file, -1)
            logging.info("Saved combined tagger in %s" % filename)
    return combined_taggers


combined_taggers = _load_combined_taggers()
