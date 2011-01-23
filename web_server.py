#!/usr/bin/env python
"""
Simple WSGI application that provides web-based chat interface.

For a demo, run this program and point your browser to
http://localhost:8080
"""

import uuid
import urlparse
import cPickle

from chatbot import Chatbot
from database import Database
from cherrypy import wsgiserver


class WebChatServer(object):
    """
    Provides web-based chat interface.  Instances of this class are
    callable WSGI applications.
    """

    def __init__(self, chatbot):
        """
        Create a new WSGI application providing a web-based chat
        interface to the given chatbot.
        """
        self.chatbot = chatbot
        self.state_datastore = {}

    def _save_conversation_state(self, conversation_state, session_id):
        """
        Store the conversation state in the key-value store.
        """
        self.state_datastore[session_id] = cPickle.dumps(conversation_state)

    def _load_conversation_state(self, session_id):
        """
        Load the conversation state from the key-value store.
        """
        return cPickle.loads(self.state_datastore[session_id])

    def __call__(self, environ, start_response):
        """
        WSGI application implementing a simple chat protocol.
        On a GET request, serve the chat interface.  On a POST, pass
        the input to the chatbot and return its response as text.
        """
        method = environ['REQUEST_METHOD']
        if method == 'GET':
            session_id = str(uuid.uuid4())
            # Start a new conversation
            (greeting, conversation_state) = self.chatbot.start_new_conversation()
            # Save the conversation state in the key-value store
            self._save_conversation_state(conversation_state, session_id)
            # Return HTML of chat interface
            start_response('200 OK', [('content-type', 'text/html')])
            template = open('chat_interface.html').read()
            template = template.replace("{{SESSION_ID}}", session_id)
            template = template.replace("{{OUTPUT}}", greeting)
            return (template, )
        elif method == 'POST':
            # Get form data
            length = int(environ.get('CONTENT_LENGTH', '0'))
            post = urlparse.parse_qs(environ['wsgi.input'].read(length))
            session_id = post['session_id'][0]
            chat_message = post['chat_message'][0]
            # Load the saved state
            conversation_state = self._load_conversation_state(session_id)
            # Get the bot's output
            output = self.chatbot.handle_input(chat_message, conversation_state)
            # Store the modified conversation state
            self._save_conversation_state(conversation_state, session_id)
            # Return the output as text
            start_response('200 OK', [('content-type', 'text/plain')])
            return (output, )


def demo():
    database = Database('sqlite:///test_database.sqlite')
    shared_chatbot = Chatbot(database)
    chat_app = WebChatServer(shared_chatbot)
    server = wsgiserver.CherryPyWSGIServer(('0.0.0.0', 8080), chat_app)
    try:
        print "Started chatbot web server."
        server.start()
    except KeyboardInterrupt:
        server.stop()
        exit()

if __name__ == "__main__":
    demo()
