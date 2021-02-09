#!/usr/bin/env python3

'''
Process raw GitHub comment string, meeting the following conditions:
- Tokenize any code blocks `console.log('This is a code block')` -> CODE
- Tokenize screen names @y3pio -> SCREEN_NAME
- Tokenize and URLS found: https://www.google.com -> URL

Pre-condition:
    Inputs the raw comment string

Post-condition:
    Outputs processed string with the above conditions met.
'''

# Download on first run.
# TODO: Transfer this to CLI startup?
import nltk
# nltk.download('wordnet')
# nltk.download('stopwords')

import spacy
import re
from string import punctuation
from nltk.stem import WordNetLemmatizer

# Generate a stopword list.
from nltk.corpus import stopwords
eng = spacy.load('en_core_web_sm')
from spacy.lang.en import English

parser = English()

stop_words = list(punctuation) + ["'s","'m","n't","'re","-","'ll",'...', "/"] + stopwords.words('english')


def get_lemma(item):
    return WordNetLemmatizer().lemmatize(item)

# Main parser/processor function

def processComment(c):
    # Tokenize CODE
    c = re.sub('```([^`]*)```|`([^`]*)`', 'CODE', c)

    # Array to store all processed string tokens
    processed_tokens = []

    # Parse them into Token using spacy parser
    parsed_line = parser(c)

    # For each token/word in the line that, tokenize the remaining URL/SCREEN_NAME
    # And also filter out words that are in the stop_words list.
    for token in parsed_line:
        if token.orth_.isspace():
            continue
        elif str(token) == "CODE":
            processed_tokens.append("CODE")
        elif token.like_url:
            processed_tokens.append('URL')
        elif token.orth_.startswith('@'):
            processed_tokens.append('SCREEN_NAME')
        elif str(token) not in stop_words:
            processed_tokens.append(get_lemma(token.lower_))

    # Return it as a string.
    return ' '.join(processed_tokens)
