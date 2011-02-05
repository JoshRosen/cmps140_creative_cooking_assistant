"""
Natural language understander.
"""
from collections import defaultdict
import inspect
import re
from nltk.stem.wordnet import WordNetLemmatizer

from data_structures import ParsedInputMessage, Message, ConversationState
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
    'egg'
    >>> normalize_ingredient_name('bing cherries')
    'bing cherry'
    """
    return LEMMATIZER.lemmatize(ingredient_name.strip())


def extract_ingredient_parts(ingredient_string):
    """
    Extracts the unit, quantity, base ingredient, and modifiers from an item in
    a recipe's ingredient list.  Returns a dictionary, or None if nothing could
    be parsed.

    >>> extract_ingredient_parts('12 cups lettuce')
    {'base_ingredient': 'lettuce', 'unit': 'cups', 'quantity': '12'}
    >>> extract_ingredient_parts("14 large, fresh eggs")
    {'base_ingredient': 'eggs', 'modifiers': 'large, fresh', 'quantity': '14'}
    """
    parts = defaultdict(lambda: None)
    tokens = ingredient_string.strip().split()
    # The first token is probably a quantity or measurement.
    parts['quantity'] = tokens.pop(0)
    if not tokens:
        return None
    # Extract unit of measurement
    unit_tokens = []
    while tokens and is_unit_of_measurement(tokens[0]):
        unit_tokens.append(tokens.pop(0))
    if unit_tokens:
        parts['unit'] = ' '.join(unit_tokens)
    if not tokens:
        return None
    # TODO: Perhaps the unit of measurement should be normalized.
    # Hopefully, the remaining tokens describe the ingredient.  There may be
    # modifiers, like 'grated cheese'.  To extract the base ingredient, use
    # WordNet.
    modifier_tokens = []
    while tokens and is_food_adjective(tokens[0].strip(',')):
        modifier_tokens.append(tokens.pop(0))
    if modifier_tokens:
        parts['modifiers'] = ' '.join(modifier_tokens)
    if not tokens:
        return None
    # TODO: Lemmatize or otherwise normalize the ingredient name.
    parts['base_ingredient'] = normalize_ingredient_name(' '.join(tokens))
    return parts


class NaturalLanguageUnderstander(object):
    """
    Object that performs natural language understanding.  No
    conversation state is stored in this object.
    
    
    >>> logger = None
    >>> conversation_state = ConversationState()
    >>> nlu = NaturalLanguageUnderstander(logger)
    
    >>> class EchoMessage(ParsedInputMessage):
    ...     frame = {'echo':None}
    ...     
    ...     def parse(self):
    ...         raw_string = self.raw_input_string
    ...         self.frame['echo'] = 'echo: %s' % raw_string
    >>> nlu.register_message(EchoMessage, conversation_state)
    >>> nlu.expect_message(EchoMessage, conversation_state)
    >>> message1 = nlu.parse_input('Rain falls from the sky. Clouds rise '
    ...                               'from the ground.', conversation_state)
    >>> message1.frame['echo']
    'echo: Rain falls from the sky. Clouds rise from the ground.'
    >>> message2 = nlu.parse_input('Natural Language gives my hives.',
    ...                             conversation_state)
    >>> message2.frame['echo']
    'echo: Natural Language gives my hives.'
    >>> nlu.acknowledge_message(conversation_state)
    """

    def __init__(self, logger):
        """
        Create a new NaturalLanguageUnderstander.
        """
        # set logger
        self.log = logger
        # unacknoweledged message stack
        self.messageStack = []
        # message classes to check input against
        self.messageTypes = []
        

    def parse_input(self, user_input, conversation_state ):
        """
        Given a string of user input and an object representing the
        conversation's state, return a ParsedInputMessage and modify
        the conversation state.
        """
        # If expecting a message, generate it
        if len(self.messageStack)>0 and self.messageStack[-1] != None:
            message = self.messageStack[-1](user_input)
            message.parse()
        else:
            # Figure out what type of message the user_input is
            message = ParsedInputMessage(user_input)
            
        return message
        
    def acknowledge_message(self, conversation_state):
        """
        Stops expecting extract_message to fillout the expected message.
        Pops the last message from the messageStack.
        """
        assert len(self.messageStack) != 0
        self.messageStack.pop()
            
    def expect_message(self, messageClass, conversation_state):
        """
        Sets extract_message to expect and fillout this message.
        Pushes this message onto the messageStack.
        """
        self.messageStack.append(messageClass)
            
    def register_message(self, messageClass, conversation_state):
        """
        Adds a message class to the types of messages to check against
        """
        assert inspect.isclass(messageClass)
        assert issubclass(messageClass, Message)

        self.messageTypes.append(messageClass)
        
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
