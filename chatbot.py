"""
Chatbot application object.
"""
from nlg import NaturalLanguageGenerator
from nlu import NaturalLanguageUnderstander
from dm import DialogueManager
from data_structures import ConversationState

class Chatbot(object):
    """
    Object that represents an instance of the chatbot application.
    This object coordinates the flow of information through the
    different modules of the application, as well as configuration
    settings.
    """

    def __init__(self, database):
        """
        Create a new instance of the chatbot application.
        """
        self.database = database
        self.nlg = NaturalLanguageGenerator()
        self.nlu = NaturalLanguageUnderstander()
        self.dm = DialogueManager(database)

    def handle_input(self, user_input, conversation_state):
        """
        Given a string of user input and an object representing the
        conversation's state, return the output string and modify the
        conversation state.
        """
        conversation_state.last_user_input = user_input
        parsed_input = self.nlu.parse_input(user_input, conversation_state)
        content_plan = self.dm.plan_response(parsed_input, conversation_state)
        bot_response = self.nlg.generate_response(content_plan, conversation_state)
        return bot_response

    def start_new_conversation(self):
        """
        Return a tuple containing an initial message and new
        conversation state.
        """
        conversation_state = ConversationState()
        return ("Hello!", conversation_state)
