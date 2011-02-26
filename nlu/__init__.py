"""
Natural language understander.
"""
import inspect
import logging
from operator import itemgetter

from data_structures import ParsedInputMessage, Message


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
    <class 'nlu.EchoMessage'>
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
