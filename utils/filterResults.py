#!/usr/bin/env python3

'''
This file contains various utility functions to help filter out our search results
'''

'''
String match result Title/Body with query string for stricter match

Pre-condition:
    - Result list, usually the list of 'items' that we get back from api call
    - And the query string param

Post-condition:
    - Returns a filtered list of the results whose title/body matches the query string
'''

from utils.io import printGHIssue

def filterIssueWithQueryString(results, query):
    matchedResults = []
    omittedResults = []

    for r in results:
        title = r['title'] or ""
        body = r['body'] or ""
        if query in  title or query in body:
            matchedResults.append(r)
        else:
            omittedResults.append(r)

    return [matchedResults, omittedResults]