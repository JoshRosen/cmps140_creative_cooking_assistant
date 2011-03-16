"""
Dialogue manager.
"""
from copy import deepcopy
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
        self.prev_query = {}
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
            return self._handle_search_message(parsed_input[0])

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

    def _handle_search_message(self, search_message):
        """
        Perform a query based on the most recent SearchMessage.
        """
        # If there's not a recipe search in progress, begin a new search:
        if not self.query:
            self.log.info("Starting new recipe search.")
            self.query = {}
            self.query['include_ingredients'] = []
            self.query['include_cuisines'] = []
            self.current_state = 'recipe_search'
        # Store the previous query, so we can revert to it if this query fails.
        self.prev_query = deepcopy(self.query)
        # Merge the new criteria with the current query.
        self.new_criteria = {}
        self.new_criteria['include_ingredients'] = []
        self.new_criteria['include_cuisines'] = []
        for ingredient_dict in search_message.frame['ingredient']:
            self.query['include_ingredients'].append(ingredient_dict['name'])
            self.new_criteria['include_ingredients'].append(ingredient_dict['name'])
        for cuisine_dict in search_message.frame['cuisine']:
            self.query['include_cuisines'].append(cuisine_dict['name'])
            self.new_criteria['include_cuisines'].append(cuisine_dict['name'])
        self.log.debug('database_query = \n%s' % str(self.query))
        # Check whether the query specifies no criteria.  If the query is
        # empty, display an error message.
        if not any(self.query.values()):
            content_plan = ContentPlanMessage("echo")
            content_plan['message'] = "I didn't understand your query."
            content_plans.append(content_plan)
            self._go_to_start_state()
            return content_plans
        # Start building up the content plan to send to the NLG.
        # Summarize the query as a form of grounding.
        content_plans = []
        content_plans.append(ContentPlanMessage('summarize_query',
                             query=self.query))
        # Search the database and remember the search results.
        self.search_results = self.db.get_recipes(**self.query)
        # Handle query success and failure:
        if not self.search_results:
            content_plans.extend(self._handle_search_failure())
        else:
            content_plans.extend(self._handle_search_success())
        return content_plans

    def _handle_search_failure(self):
        """
        Respond to a search that returned no results.
        """
        # Check if the last query specified one more ingredient.  If it did,
        # use the ontology to find alternate ingredients and suggest them to
        # the user.  TODO: only make suggestions that will result in successful
        # searches.
        if (any(self.prev_query.values()) and
            len(self.new_criteria['include_ingredients']) == 1):
            self.log.info("new_criteria specified a single include_ingredient;"
                " trying to find alternatives using ontology.")
            content_plans = []
            ingredient = self.new_criteria['include_ingredients'][0]
            content_plan = ContentPlanMessage("echo")
            content_plan['message'] = "I didn't find any with %s." % ingredient
            content_plans.append(content_plan)
            # use the ontology to find related searches that will succeed.
            ontology_node = self.db.get_ontology_node(ingredient)
            if not ontology_node:
                self.log.info("Could not find an OntologyNode for '%s'" %
                    ingredient)
                return self._handle_generic_search_failure()
            self.log.debug("Possible alternatives for '%s' are %s",
                ingredient, str([n.name for n in ontology_node.siblings]))
            def is_searchable_alternative(ingredient_name):
                test_query = deepcopy(self.prev_query)
                test_query['include_ingredients'].append(ingredient_name)
                if self.db.get_recipes(**test_query):
                    return True
                else:
                    return False
            alternatives = [n.name for n in ontology_node.siblings if
                is_searchable_alternative(n.name)]
            if not alternatives:
                self.log.info("No alternatives were searchable.")
                return self._handle_generic_search_failure()
            clarify = ContentPlanMessage('clarify')
            clarify['clarify_cat'] = ontology_node.supertype.name
            clarify['clarify_list'] = alternatives
            content_plans.append(clarify)
            self.query = self.prev_query
            return content_plans
        # Otherwise, use a generic search failure handler.
        else:
            return self._handle_generic_search_failure()

    def _handle_generic_search_failure(self):
        """
        The most general type of search failure (not a special case where we
        can offer advice using the ontology).
        """
        content_plan = ContentPlanMessage("echo")
        content_plan['message'] = \
            "I didn't find any recipes.  Let's start a new search."
        self._go_to_start_state()
        return [content_plan]

    def _handle_search_success(self):
        """
        Respond to a sucessful search (one that returend recipes).
        """
        content_plan = ContentPlanMessage("echo")
        content_plan['message'] = \
            "I found %i recipes.  Would you like to see one?" \
            "  If you want to start a new search, please say so."  \
            "  You can refine your query by specifying additional" \
            " criteria." % \
            len(self.search_results)
        return [content_plan]
