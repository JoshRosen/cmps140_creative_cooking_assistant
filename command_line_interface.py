#!/usr/bin/env python
"""
Command line interface to the chatbot.
"""
from optparse import OptionParser
from chatbot import Chatbot
from database import Database

parser = OptionParser()
parser.add_option("--database", dest="database_url",
                  default='sqlite:///test_database.sqlite')

PROMPT = "> "

def main():
    """
    Main loop for the command line interface.
    """
    (options, args) = parser.parse_args()
    database = Database(options.database_url)
    bot = Chatbot(database)
    (greeting, conversation_state) = bot.start_new_conversation()

    print greeting
    while 1:
        # Chatbot instances should not call exit() themselves.
        # If they need to exit, they should signal so, not exit
        # themselves.
        user_input = raw_input(PROMPT)
        bot_output = bot.handle_input(user_input, conversation_state)
        print bot_output


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        # Any code that needs to run on shutdown should go here.
        exit()
