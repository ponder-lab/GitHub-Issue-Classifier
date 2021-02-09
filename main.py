'''
GitHub issue mining script
- Searches for issues using the search query API.
- Filters out pull_request.
- Splits up each comments of each issues by new line.
- Store the lines as (issueID, line) tuple in an array.

TODO:
- Clean up comment line, process <CODE> tags properly.
- Feed processed comment lines into linear regression model to predict comment types.
'''
import json
from urllib.request import urlopen
from urllib.parse import urlencode

from utils.commentProcessor import processComment

def print_json(j):
	print(json.dumps(j, indent=2, sort_keys=True))

GITHUB_API_SEARCH_ISSUES_URL = "https://api.github.com/search/issues"

encodedQueryString = urlencode({
	'q': 'tf.function',
	'per_page': '10',
	'sort': 'comments',
	'order': 'desc'
})

searchUrl = GITHUB_API_SEARCH_ISSUES_URL + "?" + encodedQueryString

# Sample URL
#https://api.github.com/search/issues?q=%22%40tf.function%22&per_page=3&sort=comments&order=desc

# Actual call, be mindful of query limits on Github's api.
# searchResults = json.loads(urlopen(searchUrl)
# 	.read()
# 	.decode("utf-8"))

with open("search_sample.json") as f:
	searchResults = json.load(f)

# Sorts results by most comments to least
searchResults['items'].sort(key = lambda x: x['comments'], reverse=True)

# Slice top N issues
searchResults['items'] = searchResults['items'][0:7]

comments_urls = []

for r in searchResults['items']:
	# Only look at comments of non PR issues (pure issues)
	if not 'pull_request' in r:
		comments_urls.append({"issueID": r['id'], "comments_url": r['comments_url']})

# print(comments_urls)

# Test URL:
# https://api.github.com/repos/tensorflow/tensorflow/issues/27880/comments

# comment_data = json.loads(urlopen("https://api.github.com/repos/tensorflow/tensorflow/issues/27880/comments")
# 	.read()
# 	.decode('utf-8'))

# Hold all comment lines/text corpus as an array of tuples (issueID, commentLine)
CORPUS = []

for url in comments_urls:
	# print(str(url['issueID']) + " - " + url['comments_url'])
	comment_data = json.loads(urlopen(url['comments_url'])
	.read()
	.decode('utf-8'))

	# For each non-bot comment, split up each sentence and append into CORPUS array above.
	for comment in comment_data:
		if (comment["user"]["type"] != "Bot"):
			comment_lines = comment["body"].splitlines()

			for line in comment_lines:
				if line != "":
					CORPUS.append({ "issueID": url['issueID'], "commentLine": processComment(line)})


print_json(CORPUS)

### Load Model/Vector - Use the searilized model/count vector files included

# model = load("GitHub_comments_logisticRegression.model")

# vectorizer = load("GitHub_comments_logisticRegression.countVector")

# # TODO: Use actual comments from GitHub search results
# test_vector = vectorizer.transform([
#     "Hello this should be a test",
#     "I will start working on the changes",
#     "Reproduce the bug using the following steps",
#     "I will take on this task",
#     "I am willing to contribute",
#     "So there is no solution to this?",
#     "Any update on the progress of this task??",
#     "As an example here is a piece of code that demonstrates what I'd like to do."
# ])

# print(model.predict(test_vector))