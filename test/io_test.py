from utils.io import printGHIssue

def test_gh_issue_printer(capsys):
    testIssue = {
        'id': 12345,
        'html_url': "https://github.com/ponder-lab",
        "title": "Test Issue"
    }

    printGHIssue(testIssue)
    captured = capsys.readouterr()
    assert(captured.out == "12345 - https://github.com/ponder-lab - Test Issue\n")