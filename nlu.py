"""
Natural language understander.
"""
import inspect
from operator import itemgetter
import re
from data_structures import ParsedInputMessage, Message, ConversationState


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
            message = self.messageStack[-1]
            message.parse(user_input)
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
