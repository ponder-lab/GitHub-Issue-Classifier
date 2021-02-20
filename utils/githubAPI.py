'''
This file contains all the utility function to make HTTP calls to the API
'''
from urllib.error import HTTPError

import requests

from utils.commentProcessor import processComment

# Takes in the full URL for the search query
# Sample: https://api.github.com/search/issues?q=%22%40tf.function%22&per_page=3&sort=comments&order=desc
# Returns the results in JSON format
def gitHubSearchQueryAPI(url):
    try:
        pageResult = requests.get(url).json()
        return pageResult

    except HTTPError:
        print("Search Query HTTPError: " + url)
        exit(0)

# Given a list of issues with their comments API URL
# Query each of them and return the results in a consolidated list
def gitHubCommentAPI(issues):
    results = []
    for i in issues:
        print("[COMMENTS URL GET]: " + i['comments_url'])

        try:
            comment_data = requests.get(i['comments_url']).json()

        # We usually 403 error out here for API limit
        # Try and fix the limit of issues/comments above.
        except HTTPError:
            print("Comments API HTTPError: " + i['comments_url'])
            exit(0)

        # For each non-bot comment, split up each sentence and append into CORPUS array above.
        for comment in comment_data:
            if (comment["user"]["type"] != "Bot"):
                comment_lines = comment["body"].splitlines()

                for line in comment_lines:
                    if line != "":
                        results.append({
                            "issueID": i['issueID'],
                            "issueURL_API": comment['issue_url'],
                            "issueURL_HTML": i['issueURL_HTML'],
                            "commentLine": processComment(line),
                            "commentURL": comment['html_url']
                        })

    return results