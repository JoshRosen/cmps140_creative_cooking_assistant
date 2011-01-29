"""
Dialogue manager.
"""
from data_structures import ContentPlanMessage

class DialogueManager(object):
    """
    Object that performs dialogue management.  No conversation state
    is stored in this object.
    """

    def __init__(self, database, logger):
        """
        Create a new DialogueManager.
        """
        self.database = database
        self.log = logger

    def plan_response(self, parsed_input, conversation_state):
        """
        Given a parsed representation of user input and an object
        representing the conversation's state, return a content plan
        representing the content to be expressed in response to the
        user.
        """
        if conversation_state.current_state == 'wait_for_user_name':
            conversation_state.user_name = parsed_input.frame['user_name']
            conversation_state.current_state = 'echo_user_input'
            return ContentPlanMessage("greet_user_by_name")
        else:
            if not conversation_state.user_name:
                conversation_state.current_state = 'wait_for_user_name'
                return ContentPlanMessage("ask_for_name")
            else:
                return ContentPlanMessage("echo_user_input")
