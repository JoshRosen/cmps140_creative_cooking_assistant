"""
Natural language generator.
"""
import random
import logging
from simplenlg import NPPhraseSpec, PPPhraseSpec, SPhraseSpec, Realiser, \
    gateway, InterrogativeType
from data_structures import ContentPlanMessage


HORIZONTAL_LINE = '-' * 70


class NaturalLanguageGenerator(object):

    def __init__(self, logger):
        """
        Creates a new Natural Lanaguage Generator.

        conf_responses: a list of preconfigured templates to express
                        acknowledgement of input or action
        aff_responses: a list of preconfigured templates to express
                       affirmation or to say 'yes'
        neg_responses: a list of preconfigured templates to express
                       decline of request or action or to say 'no'
        """

        self.conf_responses = ['You got it',
                              'As you wish',
                              'You don\'t have to ask me twice',
                              'Of course',
                              'Okay',
                              'acknowledged']

        self.aff_responses = ['Yes',
                              'Yeah',
                              'Very much so',
                              'Affirmative']

        self.neg_responses = ['No',
                              'Nah',
                              'Negative',
                              'I\'m afraid not']

        self.words = {'name': 'Jeraziah',
                      'subject': 'you',
                      'verb': 'prefer',
                      'object': 'recipes',
                      'preposition': 'that contains',
                      'objmodifiers': ['Thai'],
                      'prepmodifiers': ['potatoes', 'celery', 'carrots'],
                      'adverbs': ['confidently'],
                      'lastinput': 'Sing me a song.'}
        self.log = logger
        self.log.info('NLG creation successful')

    def __getstate__(self):
        # When pickling this object, don't pickle the logger object; store its
        # name instead.
        result = self.__dict__.copy()
        result['log'] = self.log.name
        return result

    def __setstate__(self, state):
        # When unpickling this object, get a logger whose name was stored in
        # the pickle.
        self.__dict__ = state  # pylint: disable=W0201
        self.log = logging.getLogger(self.log)

    def generate_response(self, content_plan_or_plans):
        """
        Given a list of content plans representing the content to be
        expressed, return a generated utterance.  As a convience, you may pass
        a single content_plan instead of a list of content plans.

        >>> nlg = NaturalLanguageGenerator(logging.getLogger())
        >>> message1 = ContentPlanMessage('echo')
        >>> message2 = ContentPlanMessage('echo')
        >>> message1['message'] = "Hello"
        >>> message2['message'] = "World"
        >>> print nlg.generate_response(message1)
        Hello
        >>> print nlg.generate_response([message1, message2])
        Hello
        World
        """
        if isinstance(content_plan_or_plans, ContentPlanMessage):
            return self.handle_content_plan_message(content_plan_or_plans)
        response = []
        for plan in content_plan_or_plans:
            response.append(self.handle_content_plan_message(plan))
        return '\n'.join(response)

    def handle_content_plan_message(self, content_plan):
        """
        Generate an utterance from a single ContentPlanMessage.
        """
        if content_plan.msg_type == "echo":
            return content_plan['message']
        elif content_plan.msg_type == "show_recipe":
            return '\n'.join([
                self.acknowledge({}),
                self.generate_recipe(content_plan['recipe'])
            ])
        else:
            self.log.error("Don't know how to handle msg_type '%s'" %
                content_plan.msg_type)
            return ""

    def generate_recipe(self, recipe):

        """
        Receives a Recipe object and displays its contents to the user.
        """
        output = []

        output.append('Here is the recipe you requested:')
        output.append(HORIZONTAL_LINE)
        output.append(recipe.title + ' by ' + recipe.author)
        output.append(recipe.description)
        output.append('\n')
        cuisines_str = 'Cuisines: ' + \
            ', '.join(c.name for c in recipe.cuisines)
        output.append(cuisines_str)
        output.append("Servings: %s" %recipe.servings)
        if recipe.prep_time:
            output.append("Prep Time: %i minutes" % (recipe.prep_time))
        if recipe.cook_time:
            output.append("Cook Time: %i minutes" % (recipe.cook_time))
        if recipe.total_time:
            output.append("Total Time: %i minutes" % (recipe.total_time))
        output.append('\n')
        output.append(recipe.ingredients_text)
        output.append('\n')
        output.append(recipe.steps_text)
        output.append(HORIZONTAL_LINE)

        return '\n'.join(output)

    def generate(self, utter_type, keywords):
        """
        Input: a type of inquiry to create and a dictionary of keywords.
        Types of inquiries include 'what', 'who', 'where', 'why', 'how',
        and 'yes/no' questions. Alternatively, 'none' can be specified to
        generate a declarative statement.
        The dictionary is essentially divided into three core parts: the
        subject, the verb, and the object. Modifiers can be specified to these
        parts (adverbs, adjectives, etc). Additionally, an optional
        prepositional phrase can be specified.

        Example:

        >>> nlg = NaturalLanguageGenerator(logging.getLogger())
        >>> words = {'subject': 'you',
        ...         'verb': 'prefer',
        ...         'object': 'recipes',
        ...         'preposition': 'that contains',
        ...         'objmodifiers': ['Thai'],
        ...         'prepmodifiers': ['potatoes', 'celery', 'carrots'],
        ...         'adverbs': ['confidently'],
        ... }
        >>> nlg.generate('yes_no', words)
        u'Do you confidently prefer Thai recipes that contains potatoes, celery and carrots?'
        >>> nlg.generate('how', words)
        u'How do you confidently prefer Thai recipes that contains potatoes, celery and carrots?'
        """

        if utter_type.lower() == 'greet':
            if 'name' in keywords:
                return'Hello, %s!' % (keywords['name'])
            else:
                return 'Hello there!'
            return

        if utter_type.lower() == 'echo':
            if 'lastinput' in keywords:
                return keywords['lastinput']

        utterance = SPhraseSpec()
        subject = NPPhraseSpec(keywords['subject'])
        target = NPPhraseSpec(keywords['object'])
        preposition = PPPhraseSpec()

        if 'preposition' in keywords:
            preposition.setPreposition(keywords['preposition'])

        if 'prepmodifiers' in keywords:
            for modifier in keywords['prepmodifiers']:
                preposition.addComplement(modifier)

        if 'submodifiers' in keywords:
            for modifier in keywords['submodifiers']:
                subject.addModifier(modifier)

        if 'objmodifiers' in keywords:
            for modifier in keywords['objmodifiers']:
                target.addModifier(modifier)

        if utter_type.lower() == 'yes_no':
            utterance.setInterrogative(InterrogativeType.YES_NO)
        elif utter_type.lower() == 'how':
            utterance.setInterrogative(InterrogativeType.HOW)
        elif utter_type.lower() == 'what':
            utterance.setInterrogative(InterrogativeType.WHAT)
        elif utter_type.lower() == 'where':
            utterance.setInterrogative(InterrogativeType.WHERE)
        elif utter_type.lower() == 'who':
            utterance.setInterrogative(InterrogativeType.WHO)
        elif utter_type.lower() == 'why':
            utterance.setInterrogative(InterrogativeType.WHY)
        elif utter_type.lower() == 'confirm':
            return self.acknowledge(keywords)
        elif utter_type.lower() == 'affirm':
            return self.affirm(keywords)
        elif utter_type.lower() == 'decline':
            return self.decline(keywords)

        target.addModifier(preposition)
        utterance.setSubject(keywords['subject'])
        utterance.setVerb(keywords['verb'])
        if 'adverbs' in keywords:
            for modifier in keywords['adverbs']:
                utterance.addModifier(modifier)
        utterance.addComplement(target)

        realiser = Realiser()
        output = realiser.realiseDocument(utterance).strip()
        return output

    def acknowledge(self, keywords):
        """
        Returns an utterance of acknowledgement at random.
        A template is picked randomly from preconfigured choices.
        Then, the choice of adding the user's name is randomly determined.
        Finally, either a period or exclamation mark is used to end the
        sentence.
        """

        acknowledgement = random.choice(self.conf_responses)
        if 'name' in keywords:
            acknowledgement += random.choice([', ' + keywords['name'], ''])
        return acknowledgement + random.choice(['.', '!'])

    def affirm(self, keywords):
        """
        Returns an utterance of affirmation at random.
        A template is picked randomly from preconfigured choices.
        Then, the choice of adding the user's name is randomly determined.
        Finally, either a period or exclamation mark is used to end the
        sentence.
        """

        affirmation = random.choice(self.aff_responses)
        if 'name' in keywords:
            affirmation += random.choice([', ' + keywords['name'], ''])
        return affirmation + random.choice(['.', '!'])

    def decline(self, keywords):
        """
        Returns an utterance of denial or decline of action.
        A template is picked randomly from preconfigured choices.
        Then, the choice of adding the user's name is randomly determined.
        Finally, either a period or exclamation mark is used to end the
        sentence.
        """

        decline = random.choice(self.neg_responses)
        if 'name' in keywords:
            decline += random.choice([', ' + keywords['name'], ''])
        return decline + random.choice(['.', '!'])


class NLGException(Exception):
    """
    Base class for exceptions related to the NLG
    """
    pass
