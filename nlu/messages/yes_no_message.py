"""
Recognize 'yes', 'no', or phrases that mean 'yes' or 'no'.
"""
import nltk
import utils


YES_KEYWORDS = ['yes.n.01', 'okay.r.01', 'alright.s.01', 'very_well.r.02',
                'good.n.03']
NO_KEYWORDS = ['no.n.01']
MIN_DISTANCE = 3


def yes_no_message(nlu, raw_input_string):
    """
    >>> yes_no_message(None, "Hmmm... No thanks.")['confidence']
    1.0
    >>> yes_no_message(None, "Hmmm... No thanks.")['decision']
    'no'
    >>> yes_no_message(None, "Ok")['confidence']
    1.0
    >>> yes_no_message(None, "Ok")['decision']
    'yes'
    >>> yes_no_message(None, "Sounds good")['confidence']
    1.0
    >>> yes_no_message(None, "Sounds good")['decision']
    'yes'
    >>> yes_no_message(None, "I like turtles?") == None
    True
    """
    result = {
        'msg_type': 'recipe_search',
        'confidence': _yes_no_message_confidence(raw_input_string),
        'raw_input_string': raw_input_string,
        'decision': '',
        'word': '',
    }

    tokenizer = nltk.WordPunctTokenizer()
    tokenized_string = tokenizer.tokenize(raw_input_string)

    yes_distance_set = utils.min_synset_distance_in_sentence(
        YES_KEYWORDS, tokenized_string)
    no_distance_set = utils.min_synset_distance_in_sentence(
        NO_KEYWORDS, tokenized_string)

    # check MIN_DISTANCE and fill out variables
    if yes_distance_set and yes_distance_set[1] <= MIN_DISTANCE:
        (yes_set, yes_distance) = yes_distance_set
        (yes_token, yes_index) = yes_set
    else:
        yes_distance_set = None
    if no_distance_set and no_distance_set[1] <= MIN_DISTANCE:
        (no_set, no_distance) = no_distance_set
        (no_token, no_index) = no_set
    else:
        no_distance_set = None

    # check conflicts and update frame
    if yes_distance_set and no_distance_set == None:
        result['decision'] = 'yes'
        result['word'] = yes_token
    elif no_distance_set and yes_distance_set == None:
        result['decision'] = 'no'
        result['word'] = no_token
    else:  # conflict
        result['decision'] = []

    result = utils.dict_remove_empty(result)
    standard_fields = set(['msg_type', 'confidence', 'raw_input_string'])
    if set(result.keys()) - standard_fields:
        return result
    else:
        return None


def _yes_no_message_confidence(raw_input_string):
    """
    Determine confidence for yes_no_message
    """
    tokenizer = nltk.WordPunctTokenizer()
    tokenized_string = tokenizer.tokenize(raw_input_string)

    yes_distance_set = utils.min_synset_distance_in_sentence(
                        YES_KEYWORDS,
                        tokenized_string)
    no_distance_set = utils.min_synset_distance_in_sentence(
                        NO_KEYWORDS,
                        tokenized_string)

    # check min_distance
    if yes_distance_set and yes_distance_set[1] <= MIN_DISTANCE:
        return 1.0
    else:
        yes_distance_set = None
    if no_distance_set and no_distance_set[1] <= MIN_DISTANCE:
        return 1.0
    else:
        no_distance_set = None
    if yes_distance_set == None and no_distance_set == None:
        return 0.0
