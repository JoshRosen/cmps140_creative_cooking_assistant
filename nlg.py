"""
Natural language generator.
"""


class NaturalLanguageGenerator(object):
    """
    Object that performs natural language generation.  No conversation
    state is stored in this object.
    """

    def __init__(self, logger):
        """
        Create a new NaturalLanguageGenerator.
        """
        self.log = logger

    def generate_response(self, content_plan, conversation_state):
        """
        Given a content plan representing the content to be expressed
        and a conversation state, return a generated utterance and
        update the conversation state.
        """
        # TODO: implement
        # sentence planner
        # surface realizer
        if content_plan.msg_type == "ask_for_name":
            return "What's your name?"
        elif content_plan.msg_type == "echo_user_input":
            template = 'You said:\n    "%s"'
            return template % content_plan.frame['last_user_input']
        elif content_plan.msg_type == "greet_user_by_name":
            template = "It's nice to meet you, %s."
            return template % content_plan.frame['user_name']
        else:
            return "I didn't understand what you just said."
