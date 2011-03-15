"""
Grammar for extracting quantity, unit, modifiers, and base ingredient from
recipe ingredient descriptions.
"""
from pyparsing import Or, Literal, OneOrMore, nums, alphas, Regex, Word, \
    SkipTo, LineEnd, originalTextFor, Optional, ZeroOrMore, Keyword
from pyparsing_utils import LemmatizedWord
import wordlists


in_parens = Regex(r'\([^)]+\)')


modifier = Or(LemmatizedWord(w) for w in wordlists.food_adjectives if w) | in_parens \
           | Keyword("to taste")


base_ingredient = Regex(r"[^-(),][^ (),]+") + SkipTo(Keyword("to taste") | Literal(',') | Word('-') | in_parens | LineEnd())


unit = Optional(in_parens) + Or(LemmatizedWord(w)  for w in wordlists.units_of_measure if w)


quantity = OneOrMore(Word(nums + '-/'))


ingredient_line = (
    originalTextFor(Optional(quantity)).setResultsName('quantity') +
    originalTextFor(Optional(unit)).setResultsName('unit') +
    originalTextFor(ZeroOrMore(modifier + Optional(','))).setResultsName('pre_modifiers') +
    originalTextFor(base_ingredient).setResultsName('base_ingredient') +
    Optional(',') + Optional('-') +
    originalTextFor(SkipTo(LineEnd(), True)).setResultsName('post_modifiers')
)
