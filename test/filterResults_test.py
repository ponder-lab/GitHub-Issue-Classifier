from utils.filterResults import filterIssueWithQueryString

TEST_CASES = [
    {
        "items": [{
            "title": "The title contains query string alpha123",
            "body": "The body does not contain it"
        }],
        "query": "alpha123",
        "expected_result": [{
            "title": "The title contains query string alpha123",
            "body": "The body does not contain it"
        }],
        "omitted_result": []
    },
    {
        "items": [{
            "title": "The title does not contain it",
            "body": "But now the body does contain the some.function.123 query string"
        }],
        "query": "some.function.123",
        "expected_result": [{
            "title": "The title does not contain it",
            "body": "But now the body does contain the some.function.123 query string"
        }],
        "omitted_result": []
    },
    {
        "items": [{
            "title": "Neither the title",
            "body": "Or the body contains the query string"
        }],
        "query": "look@thistring",
        "expected_result": [],
        "omitted_result": [{
            "title": "Neither the title",
            "body": "Or the body contains the query string"
        }]
    },
]

def test_filter_results():
    for TEST in TEST_CASES:
        matched, omitted = filterIssueWithQueryString(TEST['items'], TEST['query'])
        assert(matched == TEST['expected_result'])
        assert(omitted == TEST['omitted_result'])