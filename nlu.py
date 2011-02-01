"""
Natural language understander.
"""
import re

from data_structures import Message


def time_to_minutes(time):
    """
    >>> time_to_minutes('3 Hrs 20 Min')
    200
    >>> time_to_minutes('1 Hour 20 Mins')
    80
    >>> time_to_minutes('10 Minutes')
    10
    """
    regex = re.compile(r"""
        (?:(\d+)\ (?:Hr|Hour)s?)?
        \ ?
        (?:(\d+)\ (?:Minute|Min)s?)?
    """, re.VERBOSE)
    match = regex.match(time)
    hours, minutes = match.groups()
    if hours == None:
        hours = 0
    if minutes == None:
        minutes = 0
    return int(minutes) + (int(hours) * 60)


class NaturalLanguageUnderstander(object):
    """
    Object that performs natural language understanding.  No
    conversation state is stored in this object.
    """

    def __init__(self, logger):
        """
        Create a new NaturalLanguageUnderstander.
        """
        self.log = logger

    def parse_input(self, user_input, conversation_state):
        """
        Given a string of user input and an object representing the
        conversation's state, return a parsed representation of the
        output string and modify the conversation state.
        """
        parsed_input = Message(msg_type=None)
        parsed_input.raw_input_string = user_input
        if conversation_state.current_state == "wait_for_user_name":
            parsed_input.frame['user_name'] = user_input
            parsed_input.msg_type = 'user_gave_name'
        return parsed_input
