################################################################################
# A set of useful tools for the exploration of nltk                            #
################################################################################

#- Synsets ---------------------------------------------------------------------

# explore_synsets
#  Lists the possible synets of a word and their corresponding hypernyms
#  WHY: pick the proper synset for the intended meaning of the word
def explore_synsets(word):
    for synset in wordnet.synsets(word):
        print synset, synset.hypernyms()
#-------------------------------------------------------------------------------
