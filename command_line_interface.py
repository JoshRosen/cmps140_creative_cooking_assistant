#!/usr/bin/env python
"""
Command line interface to the chatbot.
"""
import logging

from optparse import OptionParser

PARSER = OptionParser()
PARSER.add_option("--database", dest="database_url",
                  default='sqlite:///test_database.sqlite')
PARSER.add_option("--logfile", dest="log_filename",
                  default='cookingbot.log')

PROMPT = "> "


def main():
    """
    Main loop for the command line interface.
    """
    (options, args) = PARSER.parse_args()
    # Configure logging
    logging.basicConfig(filename=options.log_filename, level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    # These imports are performed after the logging setup because basicConfig
    # will not work if other modules call logging functions before it's called.
    from chatbot import Chatbot
    from database import Database
    # Setup the database
    db = Database(options.database_url)
    # Setup the chatbot
    logger = logging.getLogger('chatbot')
    bot = Chatbot(db, logger)
    greeting = bot.get_greeting()

    print greeting
    while 1:
        # Chatbot instances should not call exit() themselves.
        # If they need to exit, they should signal so, not exit
        # themselves.
        try:
            user_input = raw_input(PROMPT)
        except EOFError:
            return
        bot_output = bot.handle_input(user_input)
        print bot_output


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        pass
    # Any code that needs to run on shutdown should go here.
    exit()
