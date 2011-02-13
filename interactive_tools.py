"""
A set of useful tools for the exploration of nltk.
"""

#- Synsets ---------------------------------------------------------------------

def explore_synsets(word):
    """
    Lists the possible synets of a word and their corresponding hypernyms
    WHY: pick the proper synset for the intended meaning of the word
    """
    for synset in wordnet.synsets(word):
        print synset, synset.hypernyms()
