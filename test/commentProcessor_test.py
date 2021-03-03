from utils.commentProcessor import processComment

TEST_CASES = [
    {
        "test": "Hello this is a pre processed string",
        "expected_result": "hello pre processed string"
    },
    {
        "test": "This string contains a screen name @y3pio tag",
        "expected_result": "this string contains screen name SCREEN_NAME tag"
    },
    {
        "test": "Testing this url string https://test.foo.com token",
        "expected_result": "testing url string URL token"
    },
    {
        "test": "Testing for a ```multi line code block``` should be tokenized",
        "expected_result": "testing CODE tokenized"
    },
    {
        "test": "Testing for a single line `code block here` should be tokenized",
        "expected_result": "testing single line CODE tokenized"
    },
    {
        "test": "> This line is a quote, should expect a single QUOTE token",
        "expected_result": "QUOTE"
    }
]

def test_comment_processor():
    for TEST in TEST_CASES:
        assert(processComment(TEST['test'])) == TEST['expected_result']