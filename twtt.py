#!/usr/bin/env python

"""
Tweet Tokenize and Tag

This module provides the functions necessary to wrangle raw tweets data
into a form amenable to feature extraction.
"""

import re
import NLPlib
import HTMLParser


def remove_html(line):
    """
    Remove html tags and attributes (i.e. /<[^>]+>/) from a string

    Parameters
    ----------
    line : str
        A string that may contain HTML tags.

    Returns
    -------
    str
        The original string minus html tags and attributes, if it has them.

    Notes
    -----
    Use with caution.

    This function assumes the HTML is properly formed (i.e. it will fail for
    "<b class='not_closed'"). It also fails for "if 1 < 2 then 2 > 1", 
    turning it into "if 1  1".

    Examples
    --------
    >>> remove_html("<html><head>title</head></html>")
    'title'

    >>> remove_html("title</html>")
    'title'
    """
    parser = HTMLParser.HTMLParser()
    p = re.compile(r'<[^>]+>')
    return parser.unescape(p.sub('', line)).decode('utf-8')

def remove_startswith(line, remove_token, remove_word=True):
    """
    Removes a sequence of characters from a string, when they appear at the
    beginning of a word. The whole word can optionally be removed. 

    Parameters
    ----------
    line : str
        The original string from which the `remove_token` is to be removed.

    remove_token : str
        The sequence of characters to look for at the beginning of each word
        in order to decide whether or not to remove. 

    remove_work : bool
        If True, remove the entire word that starts with `remove_token`.
        If False, remove only the characters in `remove_token`. 
        Defaults to True

    Returns
    -------
    str
        A copy of the original string minus the words that start with 
        `remove_token`.

    Notes
    -----
    The lookup for the `remove_token` is case insensitive. 

    Examples
    --------
    >>> string = "use www.google.com to search"
    >>> remove_startswith(string, "www")
    'use  to search'

    >>> string = "awwwsome to search"
    >>> remove_startswith(string, "www")
    'awwwsome to search'

    >>> string = "use HtTP://google.com to search"
    >>> remove_startswith(string, "http")
    'use  to search'
    """
    if remove_word:
        regex = r"\b" + re.escape(remove_token) + r"\S+"
    else:
        regex = r"\B(" + re.escape(remove_token) + r"){1}"

    return re.sub(regex, "", line, flags=re.IGNORECASE)

def separate_clitics(line):
    """
    Separate words that contain clitics into two words by putting a space
    in between.

    Parameters
    ----------
    line : str
        A string that may contain clitics.

    Returns
    -------
    str
        A copy of the original string, where clitics words have been separated
        into two.

    Notes
    -----
    The list of clitics considered is arbitrary and may not be comprehensive.

    Examples
    --------
    >>> text = "Mr. Smith's dog doesn't bark. He'll bite instead."
    >>> separate_clitics(text)
    "Mr. Smith 's dog does n't bark. He 'll bite instead."

    >>> text = "I'd be careful if I were you. You've been warned."
    >>> separate_clitics(text)
    "I 'd be careful if I were you. You 've been warned."
    """
    clitics_regex = r'(\'s|\'re|\'m|\'ve|\'d|\'ll|n\'t|\' )'

    return re.sub(clitics_regex, r' \1', line)

def separate_sentences(line):
    """
    Split a string into a list, where each element in the list is a sentence
    from the original string.

    Parameters
    ----------
    line : str
        A string that may contain several sentences.

    Returns
    -------
    list
        A list containing all the sentences that make up the original string.

    Notes
    -----
    The sentence separation algorithm is heuristic, based on general rules of
    thumb. It may make mistakes.

    Examples
    --------
    >>> text = "Mr. Potatohead drinks 2.2 liters of water a day, i.e. " \
    ...        "he drinks a lot considering he weighs .3 grams. He is " \
    ...        "of course, a potato."
    >>> separate_sentences(text)
    ["Mr. Potatohead drinks 2.2 liters of water a day, i.e. he drinks" \
     "considering he weighs .3 grams.",
     "He is of course, a potato."]

    >>> text = "You don't believe me? I didn't think so. Sure, I could be " \
    ...        "lying... You can always look it up yourself."
    >>> separate_sentences(text)
    ["You don't believe me?",
     "I didn't think so.",
     "Sure, I could be lying...",
     "You can always look it up yourself."]
    """
    regex = r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|!)\s'

    tmp_txt = re.sub(regex, "\n", line)
    return re.split('\n+', tmp_txt)


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4 and len(sys.argv) != 3:
        msg = "Incorrect number of arguments.\n\n" \
              "usage: twtt.py input_file_path [GID] output_file_path"

        raise TypeError(msg)

    TOTAL_EXAMPLES = 1600000

    # 1. open input file (to read)
    input_file = open(sys.argv[1])

    # 2. open output file (to write)
    if len(sys.argv) == 4:
        output_file = open(sys.argv[3], "w")
 
        # 3. get the ranges for input from GID
        SUBSET_TOTAL = 11000
    
        try:
            GID = int(sys.argv[2])
        except ValueError as e:
            raise type(e)(e.message + " GID must be an integer value\n\n" + 
                          "usage: twtt.py input_file_path GID output_file_path")
    else:
        output_file = open(sys.argv[2], "w")
        GID = 0
        SUBSET_TOTAL = TOTAL_EXAMPLES

    neg_lower_bound = GID * (SUBSET_TOTAL/2)
    neg_upper_bound = ((GID + 1) * (SUBSET_TOTAL/2)) - 1
    pos_lower_bound = neg_lower_bound + (TOTAL_EXAMPLES/2)
    pos_upper_bound = neg_upper_bound + (TOTAL_EXAMPLES/2)

    tagger = NLPlib.NLPlib()

    # 4. for each line in input:
    for i, line in enumerate(input_file):
        if (neg_lower_bound <= i <= neg_upper_bound or 
            pos_lower_bound <= i <= pos_upper_bound):
            
            line = unicode(line, errors="ignore")
            fields = line.split("\",\"") 
            
            # 4.1. get sentiment (raise exception if not an int)
            target_class = fields[0][1]
 
            # 4.2. get tweet
            if fields[5].endswith("\n"):
                tweet = fields[5][:-2]
            else:
                tweet = fields[5][:-1]
           
            # 4.3. remove html tags and character codes
            tweet = remove_html(tweet)
            
            # 4.4. remove URLs
            tweet = remove_startswith(tweet, "http")
            tweet = remove_startswith(tweet, "www")

            # 4.5. remove "@" and "#" characters
            tweet = remove_startswith(tweet, "@", remove_word=False)
            tweet = remove_startswith(tweet, "#", remove_word=False)

            # 4.6. separate clitics
            tweet = separate_clitics(tweet)

            # 4.7. separate sentences
            tweet = separate_sentences(tweet)

            # 4.8. write tweet sentiment to output file
            output_file.write("<A=" + target_class + ">\n")

            # 4.9. for each sentence:
            for sentence in tweet:
                # 4.9.1. tag each token
                tokens = sentence.split()
                tags = tagger.tag(tokens)

                res = ""
                for j in range(len(tokens)):
                    res += tokens[j] + "/" + tags[j] + " "
                
                # 4.9.2. write tokenized sentence to output file
                if res:
                    output_file.write(res.encode("utf-8"))
                    output_file.write("\n")

    input_file.close()
    output_file.close()            
