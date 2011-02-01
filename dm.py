"""
Dialogue manager.
"""
from data_structures import Message


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
        # The actual DM implementation could look something like this:
        # submodules = [] # Every submodule (i.e. greeter, recipe searcher)
        #                 # implements some common interface.
        # cannidate_plans = []
        # for module in submodules:
        #     cannidate_plans.append(module.plan_response(parsed_input,
        #                                                conversation_state))
        # Decide between the cannidate plans
        # Return a plan

        # This is a simple finite state DM for demoing the chat interface.
        # This will be replaced as soon as a real DM is written.
        if conversation_state.current_state == 'wait_for_user_name':
            conversation_state.user_name = parsed_input.frame['user_name']
            conversation_state.current_state = 'echo_user_input'
            content_plan = Message("greet_user_by_name")
            content_plan.frame['user_name'] = conversation_state.user_name
            return content_plan
        else:
            if not conversation_state.user_name:
                conversation_state.current_state = 'wait_for_user_name'
                return Message("ask_for_name")
            else:
                content_plan = Message("echo_user_input")
                content_plan.frame['last_user_input'] = \
                    conversation_state.last_user_input
                return content_plan
