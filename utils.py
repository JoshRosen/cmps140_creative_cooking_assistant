import nltk

def stem_words(words, stemmer=nltk.LancasterStemmer()):
    """
    returns a stemmed list of words
    """
    return [stemmer.stem(word) for word in words]
    
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
