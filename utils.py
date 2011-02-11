import nltk

# returns a stemmed list of words
def stem_words(words, stemmer=nltk.LancasterStemmer()):
    return [stemmer.stem(word) for word in words]
