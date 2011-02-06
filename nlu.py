"""
Natural language understander.
"""
import inspect
from operator import itemgetter
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
    words = ingredient_name.strip().split()
    return ' '.join(LEMMATIZER.lemmatize(w) for w in words)


def extract_ingredient_parts(ingredient_string):
    """
    Extracts the unit, quantity, base ingredient, and modifiers from an item in
    a recipe's ingredient list.  Returns a dictionary, or None if nothing could
    be parsed.

    Simple examples:

    >>> extract_ingredient_parts('12 cups lettuce')
    {'base_ingredient': 'lettuce', 'unit': 'cups', 'quantity': '12'}
    >>> extract_ingredient_parts("14 large, fresh eggs")
    {'base_ingredient': 'egg', 'modifiers': 'large, fresh', 'quantity': '14'}

    More complex quantities:

    >>> extract_ingredient_parts('1 1/2 tbsp olive oil')
    {'base_ingredient': 'olive oil', 'unit': 'tbsp', 'quantity': '1 1/2'}
    >>> extract_ingredient_parts('1 (12 ounce) package tofu')
    {'base_ingredient': 'tofu', 'unit': '(12 ounce) package', 'quantity': '1'}
    """
    parts = {}
    ingredient_string = ingredient_string.strip()
    tokens = []
    # For tokenization, consider anything in parentheses to be a single
    # token.
    tokenize_keep_parens = r"\([^)]+\)|[a-zA-Z0-9_,.-]+"

    # Handle units and quantaties, if they are present:
    # Extract the quantity using a regular expression (to handle '1 1/2')
    match = re.match(r"^([0-9/ -]+)(.*)$", ingredient_string)
    if match:
        parts['quantity'] = match.group(1).strip()
        tokens = re.findall(tokenize_keep_parens, match.group(2))
        if not tokens:
            return None
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
        tokens = re.findall(tokenize_keep_parens, ingredient_string)
    if not tokens:
        return None

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
    # TODO: Handle modifiers that appear after the base ingredient
    parts['base_ingredient'] = normalize_ingredient_name(' '.join(tokens))
    return parts


class NaturalLanguageUnderstander(object):
    """
    Object that performs natural language understanding.  No
    conversation state is stored in this object.
    
    
    >>> logger = None
    >>> conversation_state = ConversationState()
    >>> confidenceThreshold = .5
    >>> nlu = NaturalLanguageUnderstander(confidenceThreshold, logger)
    
    >>> class EchoMessage(ParsedInputMessage):
    ...     frame = {'echo':None}
    ...     
    ...     def parse(self):
    ...         raw_string = self.raw_input_string
    ...         self.frame['echo'] = 'echo: %s' % raw_string
    ...     
    ...     @staticmethod
    ...     def confidence(raw_input_string):
    ...         return 0.0
    
    >>> nlu.register_message(EchoMessage, conversation_state)
    >>> nlu.expect_message(EchoMessage, conversation_state)
    >>> message1 = nlu.parse_input('Rain falls from the sky. Clouds rise '
    ...                               'from the ground.', conversation_state)
    >>> message1[0].frame['echo']
    'echo: Rain falls from the sky. Clouds rise from the ground.'
    >>> message2 = nlu.parse_input('Natural Language gives my hives.',
    ...                             conversation_state)
    >>> message2[0].frame['echo']
    'echo: Natural Language gives my hives.'
    >>> nlu.acknowledge_message(conversation_state)
    >>> message3 = nlu.parse_input('I like turtles...',
    ...                             conversation_state)
    >>> message3
    []
    >>> nlu.set_confidence_threshold(0.0)
    >>> message3 = nlu.parse_input('I like turtles...',
    ...                             conversation_state)
    >>> len(message3)
    1
    >>> type(message3[0])
    <class 'nlu.EchoMessage'>
    """

    def __init__(self, confidenceThreshold, logger):
        """
        Create a new NaturalLanguageUnderstander.
        """
        # set logger
        self.log = logger
        # unacknoweledged message stack
        self.messageStack = []
        # message classes to check input against
        self.messageTypes = []
        # set confidence threshold
        self.confidenceThreshold = confidenceThreshold
        

    def parse_input(self, user_input, conversation_state ):
        """
        Given a string of user input and an object representing the
        conversation's state, return a ParsedInputMessage and modify
        the conversation state.
        """
        validMessages = []
        # If expecting a message, generate it
        if len(self.messageStack)>0 and self.messageStack[-1] != None:
            message = self.messageStack[-1](user_input)
            message.parse()
            validMessages.append(message)
        else:
            # Figure out what type of message the user_input is
            # TODO: make messageType.confidence a class method
            messageTuples = [(MessageType,
                        MessageType.confidence(user_input))
                        for MessageType in self.messageTypes]
            messages = sorted(messageTuples, key=itemgetter(1))
            
            # Return the most confident message which is above threshold
            for MessageType, confidence in messages:
                if confidence >= self.confidenceThreshold:
                    message = MessageType(user_input)
                    message.parse()
                    validMessages.append(message)
            
        return validMessages
        
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
        
    def set_confidence_threshold(self, confidenceThreshold):
        """
        Sets the minimum confidence of messages acknowledge_message will return.
        """
        self.confidenceThreshold = confidenceThreshold
            
    def register_message(self, MessageClass, conversation_state):
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
