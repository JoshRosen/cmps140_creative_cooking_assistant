
"""greeter: assigns user name, selects agent, and initializes system"""
# for new users 
#    Gets and or creates a user name.
#    reloads (pickles the user's data) - for now a dummy call saying this.

# TODO:
#    When the user types in a good user name I need to recall the preferences.
#    Add good bye throughout code.
#    Add basic /profile command to code - once preferences in place.
#    Add the feedback on dishes reccommended.
#    Add pickle code to the system based on the selected user.
#    Add some crowd sourcing for cruel, affectionate sayings.
#    Integrate randomness into all utterances.
#
import re
import os
import os.path


PROMPT = '>'

def nlg(string):
    """temporary fake nlg - just prints out"""
    print(string)

help_string = """
Welcome to the %s chatbot.  We have a few minimal features to make your 
experience more pleasant.   The system keeps track of your profile as it
goes along.  That is it tries to guess what your tastes are, and uses that
information to make suggestion.  This system is still under development so
please be patient with its various quirks.  The following commands are made
available at the prompt:
   /debug - gives you a python command line promt.  This is mainly useful
        for testing.
   /profile - this will display your profile.
   /emacs - this will switch the readline xface to emacs-mode. (new user default)
   /vi - this will switch the readline xface to vi-mode.  
   /lu - will list all the existing user names.
Full source code documentation for this system can be found at:
   http://mamabot.cse.ucsc.edu/docs
Current Limitations:
   Too many to mention.
Suggestions of types of sentences that work:
   ...
If the system is being too rude to you, you may be using Helga the dominatrix 
as your agent, please change to another agent - by typing: 'I want a new agent'.
Don't use Helga if you are squeamish.

Enjoy.
"""

root_path = '.'
users_dir = '%s/new_users' % root_path
# user_name
user_name = None
# agent info.
agent_name = None 
agent_greeting = None 
agent_mode = None 

def help():
    """Provides help to the user"""
    nlg(help_string)
  
def get_feedback():
    """for returning user, asks how they liked recent recipes"""
    pass

user_max_len = 20 # come on it shouldn't be that long unless you are an excellent typist. 
user_min_len = 2

def clean_valid_user_name(user_name):
    try_user_name = user_name.strip()
    good_chars = re.search('^\s*\w[\w\d_]*\s*$', try_user_name) 
    sz = len(try_user_name)
    if good_chars and ((sz>=user_min_len) and (sz>=user_min_len)):
        return(try_user_name)
    else:
        return(None)

good_user_name_help = """
We are a bit picky.  Sorry. New user names must have between %d and %d characters, 
they must start with an alphabetic character and must be made up only of alphabetic, 
numeric characters or underscores.
""" % (user_min_len, user_max_len)

# Cruel
"I'm going to be force feeding you some recipes of my choice, you worthless s***.\n" \
+ "So be nice to me." 

"You better be nice or I will be gagging you with butter and lard."
# Do some crowd sourcing of cruel sayings.

# Affectionate ...
"Hey, why don't you come to my kitchen sometime? Please be nice you sweetie pie"


"Hi I'm Helga the best dominatrix chef in the business."  

agent_records = [
   ['Helga', 'cruel', 
                'Helga the best dominatrix chef in the business'],
   ['Marilyn', 'affectionate', 
                'Marylin Monrovia, the kindest, most affectionate chef, ever'],
   ['Kathy', 'normal', 
                'Kathy, the most straightforward and creative chef'],
]


def select_an_agent(user_name):
    """Selects an agent.  Cannot exit without selecting one. 

       We should add bye as a possible input. *EYE.
       These sets the global vars: agent_name, agent_mode, agent_greeting.
    """
    # This function assumes that these exist and are valid:
    #   dir_for_user 
    #   user_name
    global agent_name, agent_mode, agent_greeting

    msg='Please select from one of these agents:\n'
    cnt = 0
    for rec in agent_records:
        # show description of each agent.
        cnt += 1
        msg += '\t%d: %s\n' % (cnt, rec[2])
    nlg(msg)
    agent_name = None
    while agent_name is None: # loop until selection happens.
        msg = 'Please type a number for the agent between %d and %d.' \
                % (1, len(agent_records) + 1)
        nlg(msg)
        agent_no = raw_input(PROMPT)
        m = re.search('(\d)', agent_no) # look for any number. 
        if m: 
            agent_no = int(m.group(0)) - 1
            if agent_no > len(agent_records):
                nlg('\nInvalid number. Try again.')
                continue
        else:
            nlg('\nInvalid number. Try again.')
            continue
        rec = agent_records[agent_no]
        agent_name = rec[0]
        agent_greeting = "Hi I'm %s" % rec[2]
        agent_mode = rec[1]
        # save the agent.
        f = open(dir_for_user + '/agent', 'w')
        f.write(agent_name + '\n')
        f.close()
        nlg('Ok you are working with agent %s' % agent_name)
    return()

def create_new_user(user_name):
    # create_new_user is called from only one place.
    # It assumes that we have checked that the user does not exist 
    # and that the user name is valid.
    # if this completes it returns True else it returns False.
    # It defines the variables:
    #    agent_name
    #    nlg_mode
    #    and creates a users_dir
    # If a user exists it will always have an agent name.
    # right now it is put in a file.
    #
    global dir_for_user
    os.path.exists('/etc/passwd')

    if not os.path.exists(users_dir):
        # os.makedirs if intermediate levels are needed.
        os.mkdir(users_dir)
    dir_for_user = '%s/%s.usr' % (users_dir, user_name)
    if not os.path.exists(dir_for_user):
        os.mkdir(dir_for_user)
    nlg("\nOk, your user name will be %s\n" % user_name)
    select_an_agent(user_name)
    return()

def find_user(user_name):
    global agent_name, agent_mode, agent_greeting
    """finds the user and if found restores the agent info"""
    dir_for_user = '%s/%s.usr' % (users_dir, user_name)
    if os.path.exists(dir_for_user):
        agent_path = '%s/%s' % (dir_for_user, 'agent')
        f = open(agent_path, 'r')
        test_agent_name = f.readline()
        test_agent_name = test_agent_name.strip()
        for inx in range(len(agent_records)):
            rec = agent_records[inx]
            name = rec[0]
            if name == test_agent_name:
                agent_name = name 
                agent_greeting = rec[2]
                agent_mode = rec[1]
                return(True)
        return(False)            
    else:
        return(False)

def startup():
    welcome = """
    Welcome to the CREATIVE COOKING ADVISOR
    Type help at any time to get helpful hints for using our program. 
    To exit simply say: bye.  For help and hints on using the program type: help.
    """
    global user_name
    nlg(welcome)

    logged_in = False
    while not logged_in:
        # a logged in user has a user_name, a loaded profile and an agent.
        # initially a profile will just consist of an agent. That is it.
        nlg("Please enter an existing user name or type 'new' to become a "
            + "new user.")
        user_name = raw_input(PROMPT)
        wants_new_user = re.search("^\s*new\s*$", user_name, re.IGNORECASE)
        
        if wants_new_user: # to exit new user you must say good bye and start over.
            new_user = None
            nlg('As a new user you will need a user name. Please type one.')
            while not new_user:
                user_name = raw_input(PROMPT)
                new_user = clean_valid_user_name(user_name)
                if new_user is None:
                    nlg(good_user_name_help)
                    nlg('Please enter a good user name for yourself')
                    continue
    
                found_user = find_user(new_user)
                if found_user:
                    nlg('You have entered a user name that already exists.\n'
                        + 'Please enter a different new user name or type bye '
                        + 'to quit.')
                    new_user = None
                    continue
                else:
                    nlg('Thanks, that is a great user name.')

            create_new_user(new_user)
            user_name = new_user
    
        found_user = find_user(user_name)
        # defines global vars: agent_name, agent_mode, agent_greeter
        if not found_user:
            nlg('I could not find that user name.')
            continue   # starts over trying to get a user name or new.

        logged_in = True
    
        if agent_mode == 'cruel':
            hand_desc = 'strong grasping claws'
        elif agent_mode == 'affectionate':
            hand_desc = 'beautiful manicured hands'
        else: # normal
            hand_desc = 'competent hands'

        nlg("Remember that any time you can type 'help' to get helpful hints\n"
            + 'for using our system. Now I will now put you in the '  
            + '%s of chef: %s' % (hand_desc, agent_name)
        )
        nlg('Your user_name is %s, agent_name is %s, agent_mode is %s'
            + ' \nand agent_greeting is: %s' 
            % (user_name, agent_name, agent_mode, agent_greeting))

startup() 

