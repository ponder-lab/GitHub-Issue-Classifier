'''
Contains utility functions related to input/output
Everything from printing to logging to writing results to file.
'''
import json

# Simply pretty print in JSON format
def printJSON(j):
    print(json.dumps(j, indent=2, sort_keys=True))

# Prints details about a GitHub issue object
# URL, ID, Title and Body
def printGHIssue(i):
    print('%d - %s - %s' % (i['id'], i['html_url'], i['title']))