import nltk
from nltk.corpus import wordnet

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

combined_taggers = combine_backoff_taggers(
                        [nltk.TrigramTagger,
                         nltk.BigramTagger,
                         nltk.DefaultTagger('NN'),
                        ],
                        nltk.corpus.nps_chat.tagged_posts(),
                    )
