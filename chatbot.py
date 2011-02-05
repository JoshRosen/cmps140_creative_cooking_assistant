"""
Chatbot application object.
"""
import logging
from nlg import NaturalLanguageGenerator
from nlu import NaturalLanguageUnderstander
from dm import DialogueManager
from data_structures import ConversationState
from data_structures import ParsedInputMessage

# Monkey-patch the Python 2.7 logger.getChild() method into the logger class,
# to maintain backwards-compatibility with Python 2.6.
#pylint: disable=C0103
if not hasattr(logging.Logger, "getChild"):
    def _getChild(self, suffix):
        """
        Logger.getChild() method, added in Python 2.7
        """
        if self.root is not self:
            suffix = '.'.join((self.name, suffix))
        return self.manager.getLogger(suffix)
    logging.Logger.getChild = _getChild


class Chatbot(object):
    """
    Object that represents an instance of the chatbot application.
    This object coordinates the flow of information through the
    different modules of the application, as well as configuration
    settings.
    """

    def __init__(self, database, logger):
        """
        Create a new instance of the chatbot application.
        """
        self.database = database
        self.log = logger
        self.nlg = NaturalLanguageGenerator(logger.getChild('nlg'))
        self.nlu = NaturalLanguageUnderstander(0.0, logger.getChild('nlu'))
        self.dm = DialogueManager(database, logger.getChild('dm'))
        self.log.debug("Chatbot instantiated")

    def handle_input(self, user_input, conversation_state):
        """
        Given a string of user input and an object representing the
        conversation's state, return the output string and modify the
        conversation state.
        """
        self.log.info('%12s = "%s"' % ('user_input', user_input))
        conversation_state.last_user_input = user_input
        parsed_input = self.nlu.parse_input(user_input, conversation_state)
        self.log.debug('%12s = "%s"' % ('parsed_input', parsed_input))
        content_plan = self.dm.plan_response(parsed_input[0], conversation_state)
        self.log.debug('%12s = "%s"' % ('content_plan', content_plan))
        bot_response = self.nlg.generate_response(content_plan,
            conversation_state)
        self.log.info('%12s = "%s"' % ('bot_response', bot_response))
        return bot_response

    def start_new_conversation(self):
        """
        Return a tuple containing an initial message and new
        conversation state.
        """
        conversation_state = ConversationState()
        self.nlu.register_message(ParsedInputMessage, conversation_state)
        return ("Hello!", conversation_state)
