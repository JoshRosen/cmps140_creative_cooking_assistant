"""
Generators are simply canned utterance utility functions for providing
analytical support to the Messages. They have the advantage of being cached and
easily passed around.

Motivation: The NLU does not have to keep track of what each Message requires
nor execute utility functions which are not needed. Speed.
"""

from nlu.stanford_utils import get_parse_tree

import nltk
import collections

class Generators:
    """
    Simplifies using the generator classes by initializing them and providing
    easier access.
    """
    def add(self, GeneratorClass, cache_size):
        # get class name and lowercase since instance
        name = GeneratorClass.__name__.lower()
        # insert generate method into list
        setattr(self, name, GeneratorClass(cache_size, self).generate)

class Generator:
    """
    Class to cache calls to _generate.
    """
    def __init__(self, cache_size, generators):
        self.cache = collections.deque(maxlen=cache_size)
        self.generators = generators

    def _getCached(self, raw_input_string):
        for key, value in self.cache:
            if key == raw_input_string:
                return value
        return None
        
    def _putCached(self, raw_input_string, result):
        assert(self._getCached(raw_input_string) == None)
        self.cache.append((raw_input_string, result))
        
    def generate(self, raw_input_string):
        # try and lookup cache
        cached_result = self._getCached(raw_input_string)
        if cached_result:
            # return cached result
            return cached_result
        else:
            # generate, insert into cache, return result
            result = self._generate(raw_input_string, self.generators)
            self._putCached(raw_input_string, result)
            return result

    def _generate(self, raw_input_string, generators):
        raise NotImplementedError


class Generate_Tokenized_String(Generator):
    def __init__(self, cache_size, generators):
        Generator.__init__(self, cache_size, generators)
        self.tokenizer = nltk.TreebankWordTokenizer()
        
    def _generate(self, raw_input_string, generators):
        return self.tokenizer.tokenize(raw_input_string)


class Generate_Stanford_Parse_Tree(Generator):
    def _generate(self, raw_input_string, generators):
        generate_tokenized_string = generators.generate_tokenized_string
        tokenized_string = generate_tokenized_string(raw_input_string)
        return get_parse_tree(tokenized_string)
