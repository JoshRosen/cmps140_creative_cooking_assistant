"""
Natural language understander.
"""
from data_structures import ParsedInputMessage, Message, ConversationState
import inspect

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
