"""
Natural language generator.
"""
import logging


class NaturalLanguageGenerator(object):
    """
    Object that performs natural language generation.
    """

    def __init__(self, logger):
        """
        Create a new NaturalLanguageGenerator.
        """
        self.log = logger

    def __getstate__(self):
        # When pickling this object, don't pickle the logger object; store its
        # name instead.
        result = self.__dict__.copy()
        result['log'] = self.log.name
        return result

    def __setstate__(self, state):
        # When unpickling this object, get a logger whose name was stored in
        # the pickle.
        self.__dict__ = state
        self.log = logging.getLogger(self.log)

    def generate_response(self, content_plan):
        """
        Given a content plan representing the content to be expressed,
        return a generated utterance.
        """
        # TODO: implement
        # sentence planner
        # surface realizer
        if content_plan.msg_type == "echo":
            return content_plan.frame['message']
        else:
            return "I didn't understand what you just said."
