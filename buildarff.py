#!/usr/bin/env python
"""
Build arff

This module provides the functionality necessary for feature extraction
from tweets and conversion into arff format.
"""
import re


def extract_features(text, functions, parameters):
    """
    Executes the callable `functions` on the input `text` with the 
    corresponding `parameters`

    Parameters
    ----------
    text : str
        The string on which to perform the functions.
    functions : list
        A list of callables.
    parameters : list
        A list of the parameters corresponding to each
        of the callables listed in `functions`.

    Returns
    -------
    A list where each element corresponds to the result
    of the corresponding callable function.
    """
    res = []
    
    for func, params in zip(functions, parameters):
        res.append(func(text, *params))

    return res

def count_occurrences(text, regex, flags):
    """
    Counts the number of times that `regex` appears in `text` and returns the
    value converted to string.

    Parameters
    ----------
    text : str
        The string on which to count occurrences of regex.
    regex : str
        A regular expression to look for in the text.
    flags : int
        Value to pass as flags to `re.findall`

    Returns
    -------
    str 
        A string representation of the integer value resulting from counting
        the occurences of `regex` in `text`.
    """
    return str(len(re.findall(regex, text, flags=flags)))

def num_sentences(text):
    """
    Returns the number of sentences that are contained in `text`.

    Parameters
    ----------
    text : str
        The string on which to count sentences.

    Returns
    -------
    str 
        A string representation of the integer value resulting from counting
        the number of sentences in `text`.
    """
    return str(len(text.strip().split('\n')))

def avg_sentence_length(text):
    """
    Returns the average length of the senteces contained in `text`.

    Parameters
    ----------
    text : str
        The string on which to calculate the average length of its sentences.

    Returns
    -------
    str 
        A string representation of the integer value resulting from averaging
        the length of the sentences in `text`.
    """
    num_tokens = len(text.split())
    num_sentences = len(text.strip().split('\n'))

    if num_sentences > 0:
        return str(int(round(num_tokens/(1.0*num_sentences))))
    else: 
        return '0'

def avg_token_length(text):
    """
    Returns the average length of the tokens contained in `text`.

    Parameters
    ----------
    text : str
        The string on which to calculate the average length of its tokens.

    Returns
    -------
    str 
        A string representation of the integer value resulting from averaging
        the length of the tokens in `text`.
    """
    words = re.findall('(\w+)\W*\w*/{1}\S+', text.strip())
    length = len(''.join(words))
    num_tokens = len(text.split())

    if num_tokens > 0:
        return str(int(round(length/(1.0*num_tokens))))
    else: 
        return '0'

def arff_dump(relation, attributes, data, output_name):
    """
    Outputs the arff formated `relation` formed by `attributes` and `data`
    into `output_name`. In-place function: Does not return a value. 

    Parameters
    ----------
    relation : str
        The name of the relation, in accordance to [1].
    attributes : list[str, str]
        A list containing two string values. The first value corresponds to
        the name of the attribute, while the second value corresponds to
        the type of the value, in accordance to [1].
    data : list
        A list containing the values corresponding to each of the attributes
        in `attributes`, for every data entry in accordance to [1]. 
    output_name : str
        The path to the file where the output is to be written.

    Returns
    -------
    None 

    Notes
    -----
    `attributes` and `data` are assumed to be in arff format already.

    See [1] for details about the arff file format.

    References
    ----------
    [1] http://www.cs.waikato.ac.nz/ml/weka/arff.html
    """
    output_file = open(output_name, 'w')
    output_file.write('@relation ' + relation + '\n\n')
    
    for name, typ in attributes:
         output_file.write('@attribute ' + name + ' ' + typ + '\n')

    output_file.write('\n')
    output_file.write('@data\n')

    for d in data:
        output_file.write(','.join(d))
        output_file.write('\n')
    output_file.close()    


if __name__ == '__main__':
    import sys

    input_path = sys.argv[1]
    output = sys.argv[2]

    max_per_class = None
    try:
        max_per_class = int(sys.argv[3])
    except ValueError:
        raise type(e)(e.message + "max must be an integer value \n\n" +
                      "usage: buildarff.py input_file output_file [max]")
    except IndexError:
        pass

    first_person = '\W(I|me|my|mine|we|us|our|ours)/{1}\S*'
    second_person = '\W(you|your|yours|u|ur|urs)/{1}\S*'
    third_person = '\W(he|him|his|she|her|hers|it|its|they|them|their|theirs)/{1}\S*'
    coord_conj = '\S/{1}(CC)\s'
    past_tense = '\S/{1}(VBD|VBN)\s'
    future_tense = '\W*(\'ll|will|gonna{1}\S*|going/{1}\S*\s*to/{1}\S*\s*\w+/VB)\W*'
    common_nouns = '\S/{1}(NN|NNS)\s'
    proper_nouns = '\S/{1}(NNP|NNPS)\s'
    adverbs = '\S/{1}(RB|RBR|RBS)\s'
    wh_words = '\S/{1}(WDT|WP|WP$|WRB)\s'
    commas = ','
    dashes = '-'
    ellipses = '\.\.\.'
    parentheses = '\(.*\)'
    colons = ';|:'
    all_uppercase = '\W*([A-Z]{2,})/{1}\S*' # No re.IGNORECASE for this one
    slang = '\W(smh|fwb|lmfao|lmao|lms|tbh|rofl|wtf|bff|wyd|lylc|brb|atm|imao|sml|btw' \
            '|bw|imho|fyi|ppl|sob|ttyl|imo|ltr|thx|kk|omg|ttys|afn|bbs|cya|ez|f2f|gtr' \
            '|ic|jk|k|ly|ya|nm|np|plz|ru|so|tc|tmi|ym|ur|u|sol)/{1}\S*'

    # positive and negative words were counted for the bonus section
    # positive = '\W(positive|good|great|excellent|excellence|fine|nice|desirable' \
    #            '|exquisite|fabulous|ideal|marvelous|perfect|perfection' \
    #            '|splendid|wonderful|classy|elegance|elegant|beauty|beautiful' \
    #            '|dazzling|amazing|magnificent|sensational|super|superb' \
    #            '|exceptional|heavenly|powerful|entertaining|touching' \
    #            '|enjoyable|best|love|like)/{1}\S'
    # negative = '\W(negative|bad|egregious|lousy|shameful|sinful|woeful' \
    #            '|wretched|abominable|deplorable|despicable|detest|detestable' \
    #            '|dreadful|infernal|terrible|vile|dire|sinister|undesirable' \
    #            '|squalid|seamy|shoddy|sleazy|worthless|paltry|blemish|botch' \
    #            '|bungle|grievous|hopeless|ill|pathetic|poor|sad|sorry|crummy' \
    #            '|inferior|tacky|unacceptable|unsatisfactory|unworthy|awful' \
    #            '|abysmal|rotten|filthy|foul|boring|hate|worst|e+w+|yuck' \
    #            '|dislike)/{1}\S'
    # neg_emoticons = r'\W(:\(|:-\(|=\(|:\'\(|T_T|:S|:\||D:)/{1}\S'
    # pos_emoticons = r'\W(:\)|:-\)|:-D|=\)|:D|;\))/{1}\S'
    ###########################################################################

    functions = [count_occurrences for i in range(17)]
    functions.append(avg_sentence_length)
    functions.append(avg_token_length)
    functions.append(num_sentences)

    # bonus section additions
    # functions.append(count_occurrences)
    # functions.append(count_occurrences)
    # functions.append(count_occurrences)
    # functions.append(count_occurrences)
    ###########################################################################

    params = [(first_person, re.IGNORECASE|re.DOTALL), (second_person, re.IGNORECASE|re.DOTALL), 
              (third_person, re.IGNORECASE|re.DOTALL), (coord_conj, re.IGNORECASE|re.DOTALL), 
              (past_tense, re.IGNORECASE|re.DOTALL), (future_tense, re.IGNORECASE|re.DOTALL), 
              (commas, re.IGNORECASE|re.DOTALL), (colons, re.IGNORECASE|re.DOTALL), 
              (dashes, re.IGNORECASE|re.DOTALL), (parentheses, re.IGNORECASE|re.DOTALL), 
              (ellipses, re.IGNORECASE|re.DOTALL), (common_nouns, re.IGNORECASE|re.DOTALL), 
              (proper_nouns, re.IGNORECASE|re.DOTALL), (adverbs, re.IGNORECASE|re.DOTALL),
              (wh_words, re.IGNORECASE|re.DOTALL), (slang, re.IGNORECASE|re.DOTALL),
              (all_uppercase, re.DOTALL), (), (), ()]

    # bonus section additions
    # params.append((positive, re.IGNORECASE|re.DOTALL))
    # params.append((negative, re.IGNORECASE|re.DOTALL))
    # params.append((pos_emoticons, re.IGNORECASE|re.DOTALL))
    # params.append((neg_emoticons, re.IGNORECASE|re.DOTALL))
    ###########################################################################
    
    input_file = open(input_path)
    lines = re.split('<A=(.+)>', input_file.read())[1:]
    input_file.close()

    data = []
    for i in range(1, len(lines), 2):
        data.append(extract_features(lines[i], functions, params))

    for i in range(0, len(lines), 2):
        data[i/2].append(lines[i])

    # write to arff file
    relation = 'tweets'
    
    names = ['first_person', 'second_person', 'third_person', 'coord_conj',
             'past_tense', 'future_tense', 'commas', 'colons', 'dashes', 
             'parentheses', 'ellipses', 'common_nouns', 'proper_nouns',
             'adverbs', 'wh_words', 'slang', 'all_uppercase',  
             'avg_sentence_length', 'avg_token_length', 'num_sentences',
             'sentiment']
    types = ['numeric' for i in range(20)]

    # bonus section addition
    # names.insert(-1, 'pos_word_count')
    # names.insert(-1, 'neg_word_count')
    # names.insert(-1, 'pos_emoji_count')
    # names.insert(-1, 'neg_emoji_count')
    # types.append('numeric')
    # types.append('numeric')
    # types.append('numeric')
    # types.append('numeric')
    ###########################################################################

    types.append('{0, 4}')
    attributes = zip(names, types)

    if max_per_class:
        tmp_data = []
        tmp_data.extend(data[:max_per_class])
        tmp_data.extend(data[len(data)/2:(len(data)/2)+max_per_class])
        data = tmp_data[:]
    arff_dump(relation, attributes, data, output)
