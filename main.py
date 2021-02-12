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
from urllib.error import HTTPError
from urllib.parse import urlencode
from joblib import load

from utils.commentProcessor import processComment

def print_json(j):
	print(json.dumps(j, indent=2, sort_keys=True))


## Load Model/Vector - Use the searilized model/count vector files included

# model = load("GitHub_comments_logisticRegression.model")
#
# vectorizer = load("GitHub_comments_logisticRegression.countVector")
#
# # TODO: Use actual comments from GitHub search results
# test_vector = vectorizer.transform(["As an example here is a piece of code that demonstrates what I'd like to do."])
#
# print(model.predict(test_vector))

# X = [1,2,3]
#
# X = list(map(lambda a: a * 2, X))
#
# print(X)

# exit(1)

GITHUB_API_SEARCH_ISSUES_URL = "https://api.github.com/search/issues"

SEARCH_QUERY = "tf.function"

PAGES_LEFT_TO_QUERY = True

PAGE = 1

'''
GitHub limits search query to 1000 results at 100 results per page.
However, we are also querying for all the comments for each of the results we get back.

We should look to limiting our search results so that we don't get a 403 response on our
additional queries for comments.

TODO: 	Will need to look into what the optimal results we should query so that we don't
		error out on our subsequent comments_url queries. We are also filtering the top N
		issues below.
'''
MAX_PAGES_TO_QUERY = 1
RESULTS_PER_PAGE = 100
TOP_N_RESULTS = 3

while PAGES_LEFT_TO_QUERY:
	encodedQueryString = urlencode({
		'q': SEARCH_QUERY,
		'per_page': RESULTS_PER_PAGE,
		'sort': 'comments',
		'order': 'desc',
		'page': PAGE
	})

	searchUrl = GITHUB_API_SEARCH_ISSUES_URL + "?" + encodedQueryString

	# Sample URL
	#https://api.github.com/search/issues?q=%22%40tf.function%22&per_page=3&sort=comments&order=desc

	print("[SEARCH QUERY]: " + searchUrl)

	try:
		searchResults = json.loads(urlopen(searchUrl)
								   .read()
								   .decode("utf-8"))
	except HTTPError:
		print("Search Query HTTPError: " + searchUrl)
		exit(0)


	PAGE += 1

	if len(searchResults['items']) == 0 or PAGE > MAX_PAGES_TO_QUERY:
		PAGES_LEFT_TO_QUERY = False


'''
This uses a search_sample.json file results for testing/dev purpose
'''
# with open("search_sample.json") as f:
# 	searchResults = json.load(f)

# TODO: Consider refactoring the below functions to a separate utility function file
# Filter out search results that does not contain our query in the body/title
searchResults['items'] = list(filter(lambda r: SEARCH_QUERY in r['title'] or r['body'], searchResults['items']))

# Slice top N issues. This helps prevent us from hitting GitHub's API call limit.
searchResults['items'] = searchResults['items'][0:TOP_N_RESULTS]

comments_urls = []

for r in searchResults['items']:
	comments_urls.append({"issueID": r['id'], "comments_url": r['comments_url']})

# Test URL:
# https://api.github.com/repos/tensorflow/tensorflow/issues/27880/comments

# Hold all comment lines/text corpus as an array of tuples (issueID, commentLine)
CORPUS = []

for url in comments_urls:

	print("[COMMENTS URL GET]: " + url['comments_url'])

	try:
		comment_data = json.loads(urlopen(url['comments_url'])
								  .read()
								  .decode('utf-8'))

	# We usually 403 error out here for API limit
	# Try and fix the limit of issues/comments above.
	except HTTPError:
		print("Comments API HTTPError: " + url['comments_url'])
		exit(0)

	# For each non-bot comment, split up each sentence and append into CORPUS array above.
	for comment in comment_data:
		if (comment["user"]["type"] != "Bot"):
			comment_lines = comment["body"].splitlines()

			for line in comment_lines:
				if line != "":
					CORPUS.append({
						"issueID": url['issueID'],
						"issueURL_API": comment['issue_url'],
						"commentLine": processComment(line),
						"commentURL": comment['html_url']
					})


### Load Model/Vector - Use the serialized model/count vector files included
model = load("GitHub_comments_logisticRegression.model")

vectorizer = load("GitHub_comments_logisticRegression.countVector")

for c in CORPUS:
	test_vector = vectorizer.transform([c['commentLine']])
	c['category'] = model.predict(test_vector)[0]

# Print the resulting corpus with the category predicted for each comment.
print_json(CORPUS)
