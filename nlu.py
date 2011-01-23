"""
Natural language understander.
"""
from data_structures import ParsedInput

class NaturalLanguageUnderstander(object):
    """
    Object that performs natural language understanding.  No
    conversation state is stored in this object.
    """

    def __init__(self):
        """
        Create a new NaturalLanguageUnderstander.
        """
        pass

    def parse_input(self, user_input, conversation_state):
        """
        Given a string of user input and an object representing the
        conversation's state, return a parsed representation of the
        output string and modify the conversation state.
        """
        parsed_input = ParsedInput()
        if conversation_state.current_state == "wait_for_user_name":
            parsed_input['user_name'] = user_input
        return parsed_input
