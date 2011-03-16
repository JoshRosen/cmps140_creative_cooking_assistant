import logging
import re
import pprint
from nlu import NaturalLanguageUnderstander
from nlu.messages import YesNoMessage, SearchMessage, SystemMessage
from itertools import islice


LIMIT = 4 # How many messages to test


def main():
    logger = logging.getLogger()

    confidence_threshold = .5
    nlu = NaturalLanguageUnderstander(confidence_threshold, logger)

    # Register the NLU messages we want
    nlu.register_message(YesNoMessage)
    nlu.register_message(SearchMessage)
    nlu.register_message(SystemMessage)

    fil = open('INGREDIENTS.txt', 'r')

    # Skip comments and empty lines
    input_messages = (l.strip() for l in fil if not re.search('^\s*($|#)', l))
    for line in islice(input_messages, 0, LIMIT):
        messages = nlu.parse_input(line)
        print line
        for message in messages:
            print message.__class__
            print pprint.pformat(message.frame)
        print


if __name__ == '__main__':
    main()
