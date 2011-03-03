"""
Natural language understander.
"""
import inspect
import re
import logging
from operator import itemgetter
from nltk.stem.wordnet import WordNetLemmatizer

from data_structures import ParsedInputMessage, Message
# pylint:disable=E0611
from wordlists import units_of_measure, food_adjectives


LEMMATIZER = WordNetLemmatizer()


def time_to_minutes(time):
    """
    >>> time_to_minutes('3 Hrs 20 Min')
    200
    >>> time_to_minutes('1 Hour 20 Mins')
    80
    >>> time_to_minutes('10 Minutes')
    10
    """
    regex = re.compile(r"""
        (?:(\d+)\ (?:Hr|Hour)s?)?
        \ ?
        (?:(\d+)\ (?:Minute|Min)s?)?
    """, re.VERBOSE)
    match = regex.match(time)
    hours, minutes = match.groups()
    if hours == None:
        hours = 0
    if minutes == None:
        minutes = 0
    return int(minutes) + (int(hours) * 60)


def is_unit_of_measurement(word):
    """
    >>> is_unit_of_measurement('ounces')
    True
    """
    return LEMMATIZER.lemmatize(word) in units_of_measure


def is_food_adjective(word):
    """
    >>> is_food_adjective("chopped")
    True
    """
    return LEMMATIZER.lemmatize(word) in food_adjectives


def normalize_ingredient_name(ingredient_name):
    """
    Normalizes an ingredient name, removing pluralization.
    >>> normalize_ingredient_name('eggs')
    'eggs'
    >>> normalize_ingredient_name('bing cherries')
    'bing cherry'
    """
    words = ingredient_name.lower().strip().split()
    return ' '.join(LEMMATIZER.lemmatize(w) for w in words)


def tokenize_group_parens(input_string):
    """
    Tokenize the input string while treating text in parentheses as a single
    token.

    >>> tokenize_group_parens("1 (12 ounce) package")
    ['1', '(12 ounce)', 'package']
    """
    regexp = r"\([^)]+\)|[a-zA-Z0-9_,.-]+"
    return re.findall(regexp, input_string)


def extract_ingredient_parts(ingredient_string):
    """
    Extracts the unit, quantity, base ingredient, and modifiers from an item in
    a recipe's ingredient list.  Returns a dictionary, or None if nothing could
    be parsed.

    Simple examples:

    >>> extract_ingredient_parts('12 cups lettuce')
    {'base_ingredient': 'lettuce', 'unit': 'cups', 'quantity': '12'}
    >>> extract_ingredient_parts("14 large, fresh eggs")
    {'base_ingredient': 'eggs', 'modifiers': 'large, fresh', 'quantity': '14'}

    More complex quantities:

    >>> extract_ingredient_parts('1 1/2 tbsp olive oil')
    {'base_ingredient': 'olive oil', 'unit': 'tbsp', 'quantity': '1 1/2'}
    >>> extract_ingredient_parts('1 (12 ounce) package tofu')
    {'base_ingredient': 'tofu', 'unit': '(12 ounce) package', 'quantity': '1'}

    Modifiers that appear after ingredients:

    >>> extract_ingredient_parts('apple, cored, peeled')
    {'base_ingredient': 'apple', 'modifiers': 'cored, peeled'}

    TODO: handle separators like ' - ' and parentheses.

    Invalid ingredient strings:

    >>> extract_ingredient_parts('1 1/2') == None
    True
    """
    parts = {}
    ingredient_string = ingredient_string.strip()
    tokens = []

    # Handle units and quantities, if they are present:
    # Extract the quantity using a regular expression (to handle '1 1/2')
    match = re.match(r"^([0-9/ -]+)(.*)$", ingredient_string)
    if match:
        parts['quantity'] = match.group(1).strip()
        tokens = tokenize_group_parens(match.group(2))
        # Extract unit of measurement.  In cases like '1 (12 ounce) package',
        # '(12 ounce) package' is the unit of measurement.
        # TODO: Perhaps the unit of measurement should be normalized.
        unit_tokens = []
        while tokens and (is_unit_of_measurement(tokens[0]) or \
            tokens[0].startswith('(')):
            unit_tokens.append(tokens.pop(0))
        if unit_tokens:
            parts['unit'] = ' '.join(unit_tokens)
    else:
        tokens = tokenize_group_parens(ingredient_string)

    # Hopefully, the remaining tokens describe the ingredient.  There may be
    # modifiers, like 'grated cheese'.  To extract the base ingredient, use
    # WordNet.
    modifier_tokens = []
    while tokens and is_food_adjective(tokens[0].strip(',')):
        modifier_tokens.append(tokens.pop(0))
    remainder = ' '.join(tokens)
    # If we've gotten this far and run out of tokens, then the ingredient
    # string is not well-formed.
    if not remainder:
        return None
    # To deal with modifiers that appear AFTER the base ingredient, assume that
    # they are preceded by a comma.
    if ',' not in remainder:
        # No modifiers after base ingredient
        parts['base_ingredient'] = normalize_ingredient_name(remainder)
        parts['modifiers'] = ' '.join(modifier_tokens)
    else:
        # Modifiers after base ingredient
        (base_ingredient, post_modifiers) = remainder.split(',', 1)
        post_modifiers = post_modifiers.strip()
        if post_modifiers and not modifier_tokens:
            parts['modifiers'] = post_modifiers
        else:
            # If we have modifiers before and after the ingredient, separate
            # them with a comma.
            parts['modifiers'] = ', '.join([' '.join(modifier_tokens),
                post_modifiers])
        parts['base_ingredient'] = normalize_ingredient_name(base_ingredient)
    if not parts['modifiers']:
        del parts['modifiers']
    return parts


class NaturalLanguageUnderstander(object):
    """
    Object that performs natural language understanding.

    >>> logger = logging.getLogger()
    >>> confidenceThreshold = .5
    >>> nlu = NaturalLanguageUnderstander(confidenceThreshold, logger)
    
    >>> class EchoMessage(ParsedInputMessage):
    ...     frame = {'echo':None}
    ...     
    ...     def _parse(self, raw_input_string):
    ...         self.frame['echo'] = 'echo: %s' % raw_input_string
    ...     
    ...     @staticmethod
    ...     def confidence(raw_input_string):
    ...         return 0.0
    
    >>> nlu.register_message(EchoMessage)
    >>> nlu.expect_message(EchoMessage)
    >>> message1 = nlu.parse_input('Rain falls from the sky. Clouds rise '
    ...                               'from the ground.')
    >>> message1[0].frame['echo']
    'echo: Rain falls from the sky. Clouds rise from the ground.'
    >>> message2 = nlu.parse_input('Natural Language gives my hives.')
    >>> message2[0].frame['echo']
    'echo: Natural Language gives my hives.'
    >>> nlu.acknowledge_message()
    >>> message3 = nlu.parse_input('I like turtles...')
    >>> message3
    []
    >>> nlu.set_confidence_threshold(0.0)
    >>> message3 = nlu.parse_input('I like turtles...')
    >>> len(message3)
    1
    >>> type(message3[0])
    <class 'nlu.__init__.EchoMessage'>
    """

    def __init__(self, confidenceThreshold, logger):
        """
        Create a new NaturalLanguageUnderstander.
        """
        # set logger
        self.log = logger
        # expected message
        self.ExpectedMessage = None
        # message classes to check input against
        self.messageTypes = []
        # set confidence threshold
        self.confidenceThreshold = confidenceThreshold

    def __getstate__(self):
        # When pickling this object, don't pickle the logger object; store its
        # name instead.
        result = self.__dict__.copy()
        result['log'] = self.log.name
        return result

    def __setstate__(self, state):
        # When unpickling this object, get a logger whose name was stored in
        # the pickle.
        self.__dict__ = state
        self.log = logging.getLogger(self.log)

    def parse_input(self, user_input):
        """
        Given a string of user input, return a ParsedInputMessage.
        """
        validMessages = []
        # If expecting a message, generate it not matter what
        if self.ExpectedMessage != None:
            message = self.ExpectedMessage(user_input)
            validMessages.append(message)
        else:
            # Figure out what type of message the user_input is
            messageTuples = [(MessageType,
                        MessageType.confidence(user_input))
                        for MessageType in self.messageTypes]
            messages = sorted(messageTuples, key=itemgetter(1))
            
            self.log.debug('%12s = "%s"' % ('nlu.parse_input', messages))
            
            # Return sorted confident messages which are above threshold
            for MessageType, confidence in messages:
                if confidence >= self.confidenceThreshold:
                    message = MessageType(user_input)
                    validMessages.append(message)
            
        return validMessages
        
    def acknowledge_message(self):
        """
        Stops expecting extract_message to fillout the expected message.
        """
        self.ExpectedMessage = None
            
    def expect_message(self, MessageClass):
        """
        Sets extract_message to expect and fillout this message.
        """
        if self.ExpectedMessage != None:
            self.log.debug('acknowledge_message: replaced %s with %s',
                           (ExpectedMessage.__name__,
                           MessageClass.__name__))
        self.ExpectedMessage = MessageClass
        
    def set_confidence_threshold(self, confidenceThreshold):
        """
        Sets the minimum confidence of messages acknowledge_message will return.
        """
        self.confidenceThreshold = confidenceThreshold
            
    def register_message(self, MessageClass):
        """
        Adds a message class to the types of messages to check against
        """
        assert inspect.isclass(MessageClass)
        assert issubclass(MessageClass, Message)

        self.messageTypes.append(MessageClass)
        
class NaturalLanguageUnderstanderError(Exception):
    """
    Exception raised by NaturalLanguageUnderstander Object
    """
    def __init__(self, value):
        """
        Create Exception with error string
        """
        self.parameter = value
        
    def __str__(self):
        """
        Return error string
        """
        return repr(self.parameter)
