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

from math import ceil
from urllib.parse import urlencode
from joblib import load

from utils.commentProcessor import processComment
from utils.filterResults import filterIssueWithQueryString
from utils.io import printJSON, writeResultToCSV
from utils.githubAPI import gitHubSearchQueryAPI, gitHubCommentAPI

from interface import InitializeSearchInterface

'''
GitHub limits search query to 1000 results at 100 results per page.
However, we are also querying for all the comments for each of the results we get back.

We should look to limiting our search results so that we don't get a 403 response on our
additional queries for comments.

TODO: Implement authenticated API calls
https://docs.github.com/en/rest/overview/resources-in-the-rest-api#rate-limiting

Creating Personal Access Token:
https://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token
'''

#
# 1)
# Initialize CLI/Get params
#
params = InitializeSearchInterface()

PAGE = 1

SEARCH_QUERY = params['q']

max_results_param = int(params['max_results'])
pages_per_100 =  ceil(max_results_param/100)
MAX_PAGES_TO_QUERY = pages_per_100 if pages_per_100 > 1 else 1

RESULTS_PER_PAGE = 100 if max_results_param > 100 else max_results_param
SORT_BY = params['sort_by']
PRINT_LOGS = params['print_logs']
OUTPUT_FILE_PREFIX = params['out_file_prefix']


#
# 2)
# Search for issues using GitHub's search query API
#
searchResults = []
GITHUB_API_SEARCH_ISSUES_URL = "https://api.github.com/search/issues"
PAGES_LEFT_TO_QUERY = True

while PAGES_LEFT_TO_QUERY:
	encodedQueryString = urlencode({
		'q': SEARCH_QUERY,
		'per_page': RESULTS_PER_PAGE,
		'sort': SORT_BY,
		'order': 'desc',
		'page': PAGE
	})

	searchUrl = GITHUB_API_SEARCH_ISSUES_URL + "?" + encodedQueryString


	print("[SEARCH QUERY GET]: " + searchUrl)

	pageResults = gitHubSearchQueryAPI(searchUrl)

	# If no more results, stop querying additional pages.
	if len(pageResults['items']) == 0:
		PAGES_LEFT_TO_QUERY = False
	else:
		# If new incoming page results will put us over user defined search limit
		# Trim the results down to the user defined limit and stop query
		searchResults += pageResults['items']

		if len(searchResults) > max_results_param:
			searchResults = searchResults[0:max_results_param]
			PAGES_LEFT_TO_QUERY = False

	PAGE += 1

	if PAGE > MAX_PAGES_TO_QUERY:
		PAGES_LEFT_TO_QUERY = False


'''
### DEV BLOCK START
This uses a search_sample.json file results for testing/dev purpose
'''
# Hard coded params for later use
# SEARCH_QUERY = "tf.function"
# PRINT_LOGS = True
# OUTPUT_FILE_PREFIX = 'ponder'
# with open("search_sample.json") as f:
# 	searchResults = json.load(f)
'''
### DEV BLOCK END
'''

print(str(len(searchResults)) + " results retrieved.")

# Filter out search results that does not contain our query in the body/title
MATCHED_RESULTS, OMITTED_RESULTS = filterIssueWithQueryString(searchResults, SEARCH_QUERY)

print(str(len(MATCHED_RESULTS)) + " results title/body closely matched with query.")
print(str(len(OMITTED_RESULTS)) + " results omitted due to lack of match with query.")

OMITTED_ISSUES = []
for result in OMITTED_RESULTS:
	OMITTED_ISSUES.append({
		"issueID": result['id'],
		"issueURL": result['html_url'],
		"title": result['title'],
		"body": result['body']
	})

if PRINT_LOGS:
	print('\n OMITTED ISSUES \n')
	printJSON(OMITTED_ISSUES)

# Dev code to limit results to be processed to not further overload the API
# MATCHED_RESULTS = MATCHED_RESULTS[0:10]

# Test comment API URL:
# https://api.github.com/repos/tensorflow/tensorflow/issues/27880/comments

# Hold all comment lines, and tag each individual lines with the comment/issue related data
# i.e URLs, IDs, links etc...
CORPUS = []

# Hold all issues with their comments API url to query
issues_api_urls = []

for r in MATCHED_RESULTS:
	# For each issue, append to issues_api_urls the comments_url API endpoint to query the comments
	issues_api_urls.append({
		"issueID": r['id'],
		"comments_url": r['comments_url'],
		"issueURL_HTML": r['html_url']
	})

	# Also add each issue's body (description/first comment) to the
	# comment corpus array to be processed as well.
	issue_body = r['body'] or ""
	issue_body_lines = issue_body.splitlines()
	for line in issue_body_lines:
		if line != "":
			CORPUS.append({
				"issueID": r['id'],
				"issueURL_API": r['url'],
				"issueURL_HTML": r['html_url'],
				"commentLine": processComment(line),
				"commentURL": r['html_url'] # Same as issue html url
			})

print("\n")

# For each of the comment_url in the list to query, query for all the comments
# and add them to the corpus.
CORPUS += gitHubCommentAPI(issues_api_urls)

### Load Model/Vector - Use the serialized model/count vector files included
model = load("GitHub_comments_logisticRegression.model")

vectorizer = load("GitHub_comments_logisticRegression.countVector")

for c in CORPUS:
	test_vector = vectorizer.transform([c['commentLine']])
	c['category'] = model.predict(test_vector)[0]

# Print the resulting corpus with the category predicted for each comment.
if PRINT_LOGS:
	print('\n CLASSIFIED COMMENTS \n')
	printJSON(CORPUS)

print("\n")
writeResultToCSV(OMITTED_ISSUES, OUTPUT_FILE_PREFIX + '_OMITTED_ISSUES')
writeResultToCSV(CORPUS, OUTPUT_FILE_PREFIX + '_CLASSIFIED_COMMENTS')
print("\n")