"""
Natural language understander.
"""
import inspect
import re
import logging
from operator import itemgetter

from data_structures import Message
from ingredients import is_ingredient, normalize_ingredient_name, \
    extract_ingredient_parts
from nlu.generators import *


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


class NaturalLanguageUnderstander(object):
    """
    Object that performs natural language understanding.

    >>> logger = logging.getLogger()
    >>> confidenceThreshold = .5
    >>> nlu = NaturalLanguageUnderstander(confidenceThreshold, logger)

    >>> from nlu.messages.parsed_input_message import ParsedInputMessage
    >>> class EchoMessage(ParsedInputMessage):
    ...     frame = {'echo':None}
    ...     
    ...     def _parse(self, raw_input_string, generators):
    ...         self.frame['echo'] = 'echo: %s' % raw_input_string
    ...     
    ...     @staticmethod
    ...     def confidence(raw_input_string, generators):
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
    >>> isinstance(message3[0], EchoMessage)
    True
    """

    CACHE_SIZE = 16

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
        
        # initiate the generators
        # NOTE: make sure to add all generators and dependent generators before
        # use
        self.generators = Generators()
        self.generators.add(Generate_Tokenized_String, self.CACHE_SIZE)
        self.generators.add(Generate_Stanford_Parse_Tree, self.CACHE_SIZE)

    def parse_input(self, user_input):
        """
        Given a string of user input, return a ParsedInputMessage.
        """
        validMessages = []
        # If expecting a message, generate it not matter what
        if self.ExpectedMessage != None:
            message = self.ExpectedMessage(user_input, self.generators)
            validMessages.append(message)
        else:
            # Figure out what type of message the user_input is
            messageTuples = [(MessageType,
                        MessageType.confidence(user_input, self.generators))
                        for MessageType in self.messageTypes]
            messages = sorted(messageTuples, key=itemgetter(1))
            
            self.log.debug('%12s [Confidence] = "%s"' % ('nlu.parse_input', messages))
            
            # Return sorted confident messages which are above threshold
            for MessageType, confidence in messages:
                if confidence >= self.confidenceThreshold:
                    message = MessageType(user_input, self.generators)
                    self.log.debug('%12s [Parse] = "%s"' % ('nlu.parse_input', message))
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
