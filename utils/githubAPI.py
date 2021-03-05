'''
This file contains all the utility function to make HTTP calls to the API
'''
import requests
import time
import json
import re
from utils.commentProcessor import processComment
from urllib.error import HTTPError

# GLOBAL access token. getter function below.
ACCESS_TOKEN = None
def validateAccessToken(token):
    headers = {}
    headers['Authorization'] = f"token {token}"
    res = requests.get("https://api.github.com/rate_limit", headers=headers)

    return res.status_code != 401

def writeAccessToken(token):
    with open('./config/access_token.json', 'w') as config_file:
        data = {}
        data['access_token'] = token or "<YOUR_GITHUB_PERSONAL_ACCESS_TOKEN>"
        json.dump(data, config_file)

def loadAccessToken():
    with open('./config/access_token.json') as config_file:
        data = json.load(config_file)
        global ACCESS_TOKEN
        ACCESS_TOKEN = data['access_token']

def getAccessToken():
    return ACCESS_TOKEN


# Takes in the full URL for the search query
# Sample: https://api.github.com/search/issues?q=%22%40tf.function%22&per_page=3&sort=comments&order=desc
# Returns the results in JSON format
def gitHubSearchQueryAPI(url):
    try:
        headers = {}
        headers['Authorization'] = f"token {ACCESS_TOKEN}"
        pageResult = requests.get(url, headers=headers)
        pageResult.raise_for_status()

        return pageResult.json()

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
            headers = {}
            headers['Authorization'] = f"token {ACCESS_TOKEN}"
            res = requests.get(i['comments_url'], headers=headers)
            res.raise_for_status()
            comment_data = res.json()
        # We usually 403 error out here for API limit
        # Try and fix the limit of issues/comments above.
        except HTTPError:
            print("Comments API HTTPError: " + i['comments_url'])
            exit(0)

        # For each non-bot comment, split up each sentence and append into CORPUS array above.
        for comment in comment_data:
            if (comment["user"]["type"] != "Bot"):

                # Tokenize CODE before splitting lines to prevent random code formatted lines
                # to throw error and skew the results.
                code_tokenized_comment = re.sub('```([^`]*)```|`([^`]*)`', 'CODE', comment["body"])

                comment_lines = code_tokenized_comment.splitlines()
                for line in comment_lines:
                    if line:
                        results.append({
                            "issueID": i['issueID'],
                            "issueURL_API": comment['issue_url'],
                            "issueURL_HTML": i['issueURL_HTML'],
                            "commentLine": processComment(line),
                            "commentURL": comment['html_url']
                        })

    return results

def printGitHubRateLimitStatus():
    headers = {}
    if validateAccessToken(ACCESS_TOKEN):
        headers['Authorization'] = f"token {ACCESS_TOKEN}"

    res = requests.get("https://api.github.com/rate_limit", headers=headers).json()
    total = res['rate']['limit']
    remaining = res['rate']['remaining']
    reset = res['rate']['reset']

    print('\nGitHub API Query Limit')
    print(f'Total: {total}')
    print(f'Remaining: {remaining}')
    print(f'Limit Resets On: {time.ctime(reset)}\n')