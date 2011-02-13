import nltk

def stem_words(words, stemmer=nltk.LancasterStemmer()):
"""
returns a stemmed list of words
"""
    return [stemmer.stem(word) for word in words]
