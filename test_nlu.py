import cPickle
import code
import logging
import re
from nlg import NaturalLanguageGenerator
from nlu import NaturalLanguageUnderstander
from nlu.messages import *
# from dm import DialogueManager
from nlu.messages.parsed_input_message import ParsedInputMessage
from database import Database

dburl='sqlite:///test_database.sqlite'
db = Database(dburl)

logger = logging.getLogger()

nlg = NaturalLanguageGenerator(logger)
nlu = NaturalLanguageUnderstander(0.5, logger)
# dm = DialogueManager(db, logger.getChild('dm'))

confidenceThreshold = .5
nlu = NaturalLanguageUnderstander(confidenceThreshold, logger)

# Register the NLU messages we want
nlu.register_message(YesNoMessage)
nlu.register_message(SearchMessage)
nlu.register_message(SystemMessage)


fil = open('INGREDIENTS.txt', 'r')

lno = 0;
cnt = 0;
msgs = [] 
lines = [] 
input_txt = fil.readline(); lno += 1;
while input_txt:
    if re.search('^\s*($|#)', input_txt): # comment or empty lines.
        input_txt = fil.readline(); lno += 1;
        continue    # ignore empty lines
    # print('>>>>>>>>>>>>>>>>>>>>>>>>>')
    msg = nlu.parse_input(input_txt)
    lines.append(input_txt)
    msgs.append(msg)
    cnt += 1
    # print('\nL:%s' % input_txt)
    # print(msg)
    # print('<<<<<<<<<<<<<<<<<<<<<<<<<')
    input_txt = fil.readline(); lno += 1;
    if cnt > 4:
        break

def show_input(lines, msgs):
    for inx in range(len(lines)):
        print(lines[inx])
        print(msgs[inx])

show_input(lines, msgs)
