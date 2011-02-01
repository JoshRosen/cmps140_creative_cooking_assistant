"""
Data structures used for communication between modules.
"""

class ConversationState(object):
    """
    Stores all state associated with a conversation.  Instances are
    created when a conversation begins and are passed throughout the
    application.  The receiver of a ConversationState will update the
    state by modifying the ConversationState that it receives.

    The ConversationState can be persisted by pickling it using the
    pickle or cPickle modules.

    This makes it easy to put the system into specific states for
    testing, without having to write complex test setup and teardown
    methods.
    """

    def __init__(self):
        self.user_name = ""
        self.last_user_input = ""
        self.current_state = "greeting"


class Message(object):
    """
    Base class for messages exchanged between the NLU and DM and DM
    and NLG.  It implements frame-and-slot semantics through its
    frame attribute, which is a dictionary.  It also stores metadata
    using its other attributes.
    """

    def __init__(self, msg_type):
        """
        Create a new Message.
        """
        # The variable name 'type' conflicts with the Python's built-in type()
        # function.
        self.msg_type = msg_type
        # Frame implements frame-and-slot semantics.
        self.frame = {}
        # Additional metadata attributes could be added.
