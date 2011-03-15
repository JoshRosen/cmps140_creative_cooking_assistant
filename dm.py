"""
Dialogue manager.
"""
import logging
from nlg import ContentPlanMessage
from nlu.messages import SearchMessage, YesNoMessage, SystemMessage


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
        self.user_name = None
        self.current_state = 'start'
        # Possible states include 'start' and 'recipe_search'.
        self.query = {}  # The current recipe search query.
        self.search_results = []
        self._go_to_start_state()

    def _go_to_start_state(self):
        """
        Go back to the start state and reset state variables.
        """
        self.query = {}
        self.current_state = 'start'
        self.search_results = None

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
            return ContentPlanMessage("unknown")

        # For now, take first (highest confidence) message.
        # If the user is  searching for recipes:
        if isinstance(parsed_input[0], SearchMessage):
            # If there's not a recipe search in progress, begin a new search:
            if not self.query:
                self.log.info("Starting new recipe search.")
                self.query = {}
                self.query['include_ingredients'] = []
                self.query['include_cuisines'] = []
                self.current_state = 'recipe_search'
            # Merge the new criteria with the current query.
            for ingredient_dict in parsed_input[0].frame['ingredient']:
                self.query['include_ingredients'].append(ingredient_dict['name'])
            for cuisine_dict in parsed_input[0].frame['cuisine']:
                self.query['include_cuisines'].append(cuisine_dict['name'])
            self.log.debug('database_query = \n%s' % str(self.query))

            # Check whether the query specifies no criteria:
            content_plans = []
            content_plans.append(ContentPlanMessage('summarize_query',
                                 query=self.query))
            if not any(self.query.values()):
                content_plan = ContentPlanMessage("echo")
                content_plan['message'] = "I didn't understand your query."
                content_plans.append(content_plan)
                self._go_to_start_state()
                return content_plans
            # Search the database and remember the search results.
            self.search_results = self.db.get_recipes(**self.query)

            content_plan = ContentPlanMessage("echo")
            if not self.search_results:
                content_plan['message'] = \
                    "I didn't find any recipes.  Let's start a new search."
                content_plans.append(content_plan)
                self._go_to_start_state()
            else:
                content_plan['message'] = \
                    "I found %i recipes.  Would you like to see one?" \
                    "  If you want to start a new search, please say so."  \
                    "  You can refine your query by specifying additional" \
                    " criteria." % \
                    len(self.search_results)
                content_plans.append(content_plan)
            return content_plans

        # Handle system messages like 'restart' and 'exit'
        elif any(isinstance(i, SystemMessage) for i in parsed_input):
            for message in parsed_input:
                if isinstance(message, SystemMessage):
                    sys_message = message
                    break
            if sys_message.frame['action'] == 'restart':
                self._go_to_start_state()
                return ContentPlanMessage("echo",
                    message="Okay, let's start over.")
            elif sys_message.frame['action'] == 'exit':
                return ContentPlanMessage("echo",
                    message="TODO: EXIT HERE")

        # If the user answers 'yes', show them the recipes:
        elif isinstance(parsed_input[0], YesNoMessage) and self.search_results:
            if parsed_input[0].getDecision():
                return ContentPlanMessage("show_recipe",
                                          recipe=self.search_results[0])
            else:
                return ContentPlanMessage("echo",
                    message="Okay.  You can specify additional criteria or" \
                    " you can restart.")

        # Handle NLU messages that we don't know how to respond to
        else:
            return ContentPlanMessage("echo",
                message="Ask me about recipes and ingredients!")
