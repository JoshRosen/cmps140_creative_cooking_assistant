"""
Dialogue manager.
"""
import logging
from data_structures import ContentPlanMessage
from nlu.messages import SearchMessage, YesNoMessage


class DialogueManager(object):
    """
    Object that performs dialogue management.
    """

    def __init__(self, db, logger):
        """
        Create a new DialogueManager.
        """
        self.db = db
        self.log = logger
        self.current_state = None
        self.search_results = None
        self.user_name = None

    def __getstate__(self):
        # When pickling this object, don't pickle the logger object; store its
        # name instead.
        result = self.__dict__.copy()
        result['log'] = self.log.name
        return result

    def __setstate__(self, state):
        # When unpickling this object, get a logger whose name was stored in
        # the pickle.
        self.__dict__ = state  # pylint: disable=W0201
        self.log = logging.getLogger(self.log)

    def plan_response(self, parsed_input):
        """
        Given a list of parsed representations of user input, return a content
        plan representing the content to be expressed in response to the user.
        """
        # This is a very simple, dummy dialog manager.  It's better than the
        # "What is your name" demo that we had before.  Right now, it allows
        # users to search for recipes and choose whether or not they want to
        # display the titles of the recipes in the search results.  It doesn't
        # use the NLG yet; it uses a special 'echo' message that passes strings
        # through the NLG to the user.

        # If we didn't understand the user:
        if not parsed_input:
            content_plan = ContentPlanMessage("echo")
            content_plan['message'] = "Could you explain that again?"
            return content_plan

        # For now, take first (highest confidence) message.
        # If the user is  searching for recipes:
        if isinstance(parsed_input[0], SearchMessage):
            # Construct a database query.
            query = {}
            query['include_ingredients'] = []
            query['include_cuisines'] = []
            for ingredient_dict in parsed_input[0].frame['ingredient']:
                query['include_ingredients'].append(ingredient_dict['name'])
            for cuisine_dict in parsed_input[0].frame['cuisine']:
                query['include_cuisines'].append(cuisine_dict['name'])
            self.log.debug('database_query = \n%s' % str(query))
            # Check whether the query specifies no criteria:
            if not any(query.values()):
                content_plan = ContentPlanMessage("echo")
                content_plan['message'] = "I didn't understand your query."
                return content_plan
            # Search the database and remember the search results.
            self.search_results = self.db.get_recipes(**query)

            content_plan = ContentPlanMessage("echo")
            if not self.search_results:
                content_plan['message'] = "I didn't find any recipes."
            else:
                content_plan['message'] = \
                    "I found %i recipes.  Would you like to see one?" % \
                    len(self.search_results)
            return content_plan

        # If the user answers 'yes', show them the recipes:
        elif isinstance(parsed_input[0], YesNoMessage) and self.search_results:
            if parsed_input[0].getDecision():
                content_plan = ContentPlanMessage("show_recipe")
                content_plan['recipe'] = self.search_results[0]
            else:
                content_plan = ContentPlanMessage("echo")
                content_plan['message'] = "Okay.  Let's restart."
            self.search_results = None
            return content_plan

        # Handle NLU messages that we don't know how to respond to
        else:
            content_plan = ContentPlanMessage("echo")
            content_plan['message'] = \
                "Ask me about recipes and ingredients!"
            return content_plan
