import argparse
import re

from math import ceil
from urllib.parse import urlencode
from joblib import load

from utils.commentProcessor import processComment
from utils.filterResults import filterIssueWithQueryString
from utils.io import printJSON, writeResultToCSV
from utils.githubAPI import gitHubSearchQueryAPI, gitHubCommentAPI, loadAccessToken

from interface import InitializeSearchInterface

#
# 0)
# Setup argparser to figure out if user wants to use pyinquirer
# or to just pass in the args via argparser
#
def sort_by_arg_checker(arg_value):
	valid_options = ["comments", "best-match"]

	if arg_value not in valid_options:
		raise argparse.ArgumentTypeError

	return arg_value
parser = argparse.ArgumentParser()

# Interface option, if true we toggle the interface below.
# If false, we just grab the params from argparser result.
parser.add_argument('-i', '--interactive', action='store_true',
					help="**toggle the interactive CLI**")

parser.add_argument('query')

parser.add_argument('-v', '--verbose', action='store_true',
					help="print additional logs")
parser.add_argument('-m', '--max-results',
					type=int,
					default=1000,
					help="(int) max results to query")
parser.add_argument('-s', '--sort-by',
					type=sort_by_arg_checker,
					default='comments',
					help='sort by one of: [comments, best-match]')
parser.add_argument('-p', '--prefix-filename',
					default="results_",
					help='(string) file name prefix for result output files')
args = parser.parse_args()

#
# 1)
# Initialize CLI/Get params
#

params = {}

# If user entered the '-i' or '--interface' option, trigger the pyinquirer interactive interface.
if args.interactive:
	params = InitializeSearchInterface(args.query)
else:
	params['q'] = args.query
	params['max_results'] = args.max_results
	params['sort_by'] = args.sort_by
	params['print_logs'] = args.verbose
	params['out_file_prefix'] = args.prefix_filename

PAGE = 1

SEARCH_QUERY = params['q']

max_results_param = int(params['max_results'])
pages_per_100 =  ceil(max_results_param/100)
MAX_PAGES_TO_QUERY = pages_per_100 if pages_per_100 > 1 else 1

RESULTS_PER_PAGE = 100 if max_results_param > 100 else max_results_param
SORT_BY = params['sort_by']
PRINT_LOGS = params['print_logs']
OUTPUT_FILE_PREFIX = params['out_file_prefix']

# Load GitHub personal access token into memory.
loadAccessToken()

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

#
# 3)
# Omit any search results that whose body/title does not contain our search query
# Checks for substring match
#
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

'''
### DEV BLOCK START
This slices the first 10 matches so we don't overload GitHub's API limit
'''
# Dev code to limit results to be processed to not further overload the API
# MATCHED_RESULTS = MATCHED_RESULTS[0:10]

# Test comment API URL:
# https://api.github.com/repos/tensorflow/tensorflow/issues/27880/comments
'''
### DEV BLOCK END
'''

#
# 4)
# For each of the results (MATCHED_RESULTS) that matches our query
# Fetch their comments and clean/tokenize them.
#

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
	# Also check for issue's description for any CODE blocks to be tokenized.
	issue_body = re.sub('```([^`]*)```|`([^`]*)`', 'CODE', issue_body)
	issue_body_lines = issue_body.splitlines()
	for line in issue_body_lines:
		# Strip away any new lines
		line = line.strip('\n')
		line = line.strip('\t')
		if line:
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

#
# 5)
# Once we have fetch all the comments, and split them up into lines and tokenized them
# Load the prediction model from the serialized file and predict the comments.
#
### Load Model/Vector - Use the serialized model/count vector files included
model = load("models/GitHub_comments_logisticRegression.model")

vectorizer = load("models/GitHub_comments_logisticRegression.countVector")

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