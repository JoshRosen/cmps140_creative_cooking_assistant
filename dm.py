"""
Dialogue manager.
"""
import logging
from data_structures import ContentPlanMessage


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
        self.__dict__ = state
        self.log = logging.getLogger(self.log)

    def plan_response(self, parsed_input):
        """
        Given a list of parsed representations of user input, return a content
        plan representing the content to be expressed in response to the user.
        """
        # The actual DM implementation could look something like this:
        # submodules = [] # Every submodule (i.e. greeter, recipe searcher)
        #                 # implements some common interface.
        # cannidate_plans = []
        # for module in submodules:
        #     cannidate_plans.append(module.plan_response(parsed_input))
        # Decide between the cannidate plans
        # Return a plan

        # This is a simple finite state DM for demoing the chat interface.
        # This will be replaced as soon as a real DM is written.
        
        # Currently this does not take advantage of message types
        
        if self.current_state == 'wait_for_user_name':
            self.user_name = parsed_input[0]['raw_input_string']
            self.current_state = 'echo_user_input'
            content_plan = ContentPlanMessage("greet_user_by_name")
            content_plan.frame['user_name'] = self.user_name
            return content_plan
        else:
            if not self.user_name:
                self.current_state = 'wait_for_user_name'
                return ContentPlanMessage("ask_for_name")
            else:
                content_plan = ContentPlanMessage("echo_user_input")
                content_plan.frame['last_user_input'] = \
                    parsed_input[0]['raw_input_string']
                return content_plan
