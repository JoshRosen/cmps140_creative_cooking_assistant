"""
Natural language understander.
"""
import logging
from operator import itemgetter


class NaturalLanguageUnderstander(object):
    """
    Object that performs natural language understanding.

    The semantic frame generation takes place in functions that are passed to
    the NLU and called when it's trying to understand an input utterance.
    These functions return None if they can't generate a frame, or return
    a dictionary with a 'msg_type' indicating the message's type,
    a 'confidence' value that ranges between 0.0 and 1.0 and represents the
    function's confidence in its parsing, and a 'raw_input_string' value that
    holds the input passed to the message function.

    Each function takes a NaturalLanguageUnderstander instance as its first
    argument; this allows the functions to retrieve salience information from
    the NLU for use in resolving pronouns.

    As a very simple example of a message function used by the NLU:

    >>> def yes_no_message(nlu, input_string):
    ...    result = {'msg_type': 'yes_no', 'confidence': 1.0,
    ...              'raw_input_string': input_string}
    ...    if input_string == 'yes':
    ...        result['answer'] = 'yes'
    ...        return result
    ...    elif input_string == 'no':
    ...        result['answer'] = 'no'
    ...        return result
    ...    else:
    ...        return None

    To use the NLU, create a NaturalLanguageUnderstander object, register the
    messages that you want it to recognize, and call its parse_input() method:

    >>> logger = logging.getLogger()
    >>> confidence_threshold = .5
    >>> nlu = NaturalLanguageUnderstander(confidence_threshold, logger)
    >>> nlu.register_message(yes_no_message)
    >>> messages = nlu.parse_input('yes')
    >>> messages[0]['msg_type']
    'yes_no'
    >>> messages[0]['answer']
    'yes'
    >>> nlu.parse_input("I'd like a cookie.")[0]['msg_type']
    'out_of_domain'

    >>> from nlu.messages import recipe_search_message
    >>> nlu.register_message(recipe_search_message)
    >>> messages = nlu.parse_input("I'd like a breakfast recipe.")
    >>> messages[0]['msg_type']
    'recipe_search'
    >>> messages[0]['meals']
    ['breakfast']

    >>> nlu.expect_message(yes_no_message)
    >>> nlu.parse_input("I'd like a breakfast recipe.")
    [None]
    """

    def __init__(self, confidence_threshold, logger):
        """
        Create a new NaturalLanguageUnderstander.
        """
        # set logger
        self.log = logger
        # expected message
        self.expected_message = None
        # Message functions to check input against
        self.message_functions = set()
        # set confidence threshold
        self.confidence_threshold = confidence_threshold

    def __getstate__(self):
        # When pickling this object, don't pickle the logger object; store its
        # name instead.
        result = self.__dict__.copy()
        result['log'] = self.log.name
        return result

    def __setstate__(self, state):
        # When unpickling this object, get a logger whose name was stored in
        # the pickle.
        self.__dict__ = state  # pylint: disable-msg=W0201
        self.log = logging.getLogger(self.log)

    def parse_input(self, user_input):
        """
        Given a string of user input, return a dictionary representing the
        frame semantics extracted from the user input.
        """
        # If expecting a message, generate it not matter what
        if self.expected_message:
            # TODO: how should we handle failure here?  Return an
            # 'out_of_domain' message?
            return [self.expected_message(self, user_input)]
        else:
            # Figure out what type of message the user_input is
            # It might be a good idea to use short-circuit evaluation here and
            # stop after we get a confidence = 1 message.
            messages = [f(self, user_input) for f in self.message_functions]
            messages = [m for m in messages if m]  # Throw out None messages.
            messages = sorted(messages, key=itemgetter('confidence'))

            self.log.debug('parse_input = %s' % messages)

            # Return messages with confidence scores above confidence_threshold
            messages = [m for m in messages if m['confidence'] >=
                        self.confidence_threshold]
            if not messages:
                return [{'msg_type': 'out_of_domain', 'confidence': 1,
                         'raw_input_string': user_input}]
            else:
                return messages

    def acknowledge_message(self):
        """
        Stops expecting extract_message to fillout the expected message.
        """
        self.expected_message = None

    def expect_message(self, message_function):
        """
        Sets extract_message to expect and fillout this message.
        """
        if self.expected_message:
            self.log.debug('acknowledge_message: replaced %s with %s',
                           (self.expected_message.__name__,
                           message_function.__name__))
        self.expected_message = message_function

    def set_confidence_threshold(self, confidence_threshold):
        """
        Sets the minimum confidence of messages acknowledge_message will
        return.
        """
        self.confidence_threshold = confidence_threshold

    def register_message(self, message_function):
        """
        Adds a message function to the set of messages to check against.
        """
        if message_function in self.message_functions:
            self.log.debug("Registering an already-registered message: %s",
                message_function.__name__)
        self.message_functions.add(message_function)


class NaturalLanguageUnderstanderError(Exception):
    """
    Exception raised by NaturalLanguageUnderstander Object
    """
    pass
