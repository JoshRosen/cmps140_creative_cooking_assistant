"""
Tools for working with Pyparsing.

Pyparsing is a nice library; there's a good guide at
http://pyparsing.wikispaces.com/HowToUsePyparsing
"""
from pyparsing import Token, ZeroOrMore, Literal
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import wordnet


LEMMATIZER = WordNetLemmatizer()


# Custom ParserElement Subclasses


class LemmatizedWord(Token):
    """
    Matches lemmatized words.
    This code is adapted from pyparsing's CaselessKeyword implementation.

    >>> LemmatizedWord('apple').parseString('apples')
    (['apples'], {})
    >>> l = ZeroOrMore(LemmatizedWord('apple'))
    >>> l.parseString('    apples  apple')
    (['apples', 'apple'], {})
    """

    def __init__(self, matchLemma):
        super(LemmatizedWord, self).__init__()
        self.matchLemma = matchLemma
        self.name = '"LemmatizedWord: %s"' % self.matchLemma
        self.errmsg = "Expected something that lemmatizes to '%s'" % matchLemma

    def parseImpl(self, instring, loc, doActions=True):
        # Optimization: If the first character of the input string and the
        # lemmatized word don't match, then fail immediately:
        if instring[loc] != self.matchLemma[0]:
            exc = self.myException
            exc.loc = loc
            exc.pstr = instring
            raise exc
        # Search until the end of the token / word boundary.
        word_boundary_tokens = "., "
        matchLen = 1
        while (loc+matchLen < len(instring) and
            instring[loc+matchLen] not in word_boundary_tokens):
            matchLen += 1
        stringToMatch = instring[loc:loc+matchLen]
        if LEMMATIZER.lemmatize(stringToMatch) == self.matchLemma:
            return loc+matchLen, stringToMatch
        exc = self.myException
        exc.loc = loc
        exc.pstr = instring
        raise exc


# This is an experiment; there might be a better way to do this:
class InSynset(Token):
    """
    Match words that are in the given synset.

    >>> InSynset('meal.n.01').parseString('repast')
    (['repast'], {})
    >>> InSynset('meal.n.01').parseString('repast')
    (['repast'], {})
    >>> w = Literal("I") + InSynset('want.v.02') + Literal("a recipe.")
    >>> w.parseString("I need a recipe.")
    (['I', 'need', 'a recipe.'], {})
    >>> InSynset('meal.n.01').parseString('apple') #doctest: +IGNORE_EXCEPTION_DETAIL
    Traceback (most recent call last):
    ParseException: Expected something in synset 'meal.n.01' (at char 0), ...
    """

    def __init__(self, matchSynset):
        super(InSynset, self).__init__()
        self.matchSynset = wordnet.synset(matchSynset)
        self.name = '"InSynset: %s"' % self.matchSynset
        self.errmsg = "Expected something in synset '%s'" % matchSynset

    def parseImpl(self, instring, loc, doActions=True):
        # Search until the end of the token / word boundary.
        word_boundary_tokens = "., "
        matchLen = 1
        while (loc+matchLen < len(instring) and
            instring[loc+matchLen] not in word_boundary_tokens):
            matchLen += 1
        stringToMatch = instring[loc:loc+matchLen]
        for wordSynset in wordnet.synsets(stringToMatch):
            if wordSynset == self.matchSynset:
                return loc+matchLen, stringToMatch
        exc = self.myException
        exc.loc = loc
        exc.pstr = instring
        raise exc
