"""
Natural language understander.
"""
from data_structures import Message


class NaturalLanguageUnderstander(object):
    """
    Object that performs natural language understanding.  No
    conversation state is stored in this object.
    """

    def __init__(self, logger):
        """
        Create a new NaturalLanguageUnderstander.
        """
        self.log = logger

    def parse_input(self, user_input, conversation_state):
        """
        Given a string of user input and an object representing the
        conversation's state, return a parsed representation of the
        output string and modify the conversation state.
        """
        parsed_input = Message(msg_type=None)
        parsed_input.raw_input_string = user_input
        if conversation_state.current_state == "wait_for_user_name":
            parsed_input.frame['user_name'] = user_input
            parsed_input.msg_type = 'user_gave_name'
        return parsed_input
