from pyfiglet import Figlet
from PyInquirer import prompt
from prompt_toolkit.validation import Validator, ValidationError
from utils.io import clear
from utils.githubAPI import loadAccessToken,\
    writeAccessToken,\
    getAccessToken,\
    validateAccessToken,\
    printGitHubRateLimitStatus
import regex

# Params validator
class NonEmptyStringValidator(Validator):
    def validate(self, document):
        if not document.text.replace(' ', ''):
            raise ValidationError(
                message='Please enter a non-empty string',
                cursor_position=0)

class MaxResultValidator(Validator):
    def validate(self, document):
        ok = regex.match('^([1-9]|[1-9][0-9]|[1-9][0-9][0-9]|1000)$', document.text)
        if not ok:
            raise ValidationError(
                message='Please enter max results range (1-1000)',
                cursor_position=len(document.text))  # Move cursor to end

SORT_OPTIONS_MAP = {
    'Best Match': 'best-match',
    'Comments': 'comments'
}

# Question Interface
INTERFACE = [
    {
        'type': 'input',
        'name': 'q',
        'message': "Enter search string:",
        'validate': NonEmptyStringValidator
    },
    {
        'type': 'input',
        'name': 'out_file_prefix',
        'message': "Enter a prefix for results output file:",
        'validate': NonEmptyStringValidator
    },
    {
        'type': 'input',
        'name': 'max_results',
        'message': "Max number of results (1-1000):",
        'validate': MaxResultValidator
    },
    {
        'type': 'list',
        'name': 'sort_by',
        'message': "Sort by:",
        'choices': ['Best Match', 'Comments'],
        'filter': lambda val: SORT_OPTIONS_MAP[val]
    },
    {
        'type': 'checkbox',
        'name': 'filter',
        'message': "Categories to filter out:",
        'choices': [
            {
                'name': 'Expected Behaviour'
            },
            {
                'name': 'Motivation'
            },
            {
                'name': 'Observed Bug Behaviour'
            },
            {
                'name': 'Bug Reproduction'
            },
            {
                'name': 'Investigation and Exploration'
            },
            {
                'name': 'Solution Discussion'
            },
            {
                'name': 'Contribution and Commitment'
            },
            {
                'name': 'Task Progression'
            },
            {
                'name': 'Testing'
            },
            {
                'name': 'Future Plan'
            },
            {
                'name': 'New Issues and Requests'
            },
            {
                'name': 'Solution Usage'
            },
            {
                'name': 'WorkArounds'
            },
            {
                'name': 'Issue Content Management'
            },
            {
                'name': 'Action on Issue'
            },
            {
                'name': 'Social Conversation'
            }
        ]
    },
    {
        'type': 'confirm',
        'name': 'print_logs',
        'message': "Print logs to console/terminal? (y/N):",
    }
]

CONFIRM_INTERFACE = [
    {
        'type': 'confirm',
        'name': 'is_finalized',
        'message': "Confirm above query (y/N):",
    }
]

# Adding personal access token interface
ADD_TOKEN_INTERFACE = [
    {
        'type': 'confirm',
        'name': 'add_token',
        'message': "It looks like you don't have a personal access token set properly!"
                   "\n(Either not set properly in config.json, or is an invalid token)"
                   "\n\nIt is HIGHLY recommended that you add a personal access token"
                   "\nto increase your GitHub API query limit (5000 for authenticated queries)."
                   "\nFollow these instructions to create a GitHub Personal Access Token"
                   "\nhttps://docs.github.com/en/github/authenticating-to-github/creating-a-personal-access-token"
                   "\n\nWould you like to add a token? (Y/n)",
        'default': True
    },
    {
        'type': 'input',
        'name': 'access_token',
        'message': "Enter your access token:",
        'when': lambda answers: answers.get('add_token', True)
    },
]

ADD_VALID_TOKEN_INTERFACE = [
    {
        'type': 'confirm',
        'name': 'retry_add_token',
        'message': "Token not valid, would you like to try again? (Y/n)",
        'default': True
    },
    {
        'type': 'input',
        'name': 'access_token',
        'message': "Enter your access token:",
        'when': lambda answers: answers.get('retry_add_token', True)
    },
]

# Print CLI header
def printHeader():
    f = Figlet(font='big')
    print(f.renderText('GitHub Issue Classifier'))
    print('GitHub Issue Classifier CLI Tool')
    print('PONDER Lab - https://github.com/ponder-lab \n')

# Main Interface Function
def InitializeSearchInterface(default_query=''):

    # Check if personal access token is configured.

    # Load access token into memory from file and set it to global ACCESS_TOKEN
    loadAccessToken()

    # Get global ACCESS_TOKEN variable from the GitHub API file.
    ACCESS_TOKEN = getAccessToken()
    is_token_valid = validateAccessToken(ACCESS_TOKEN)
    # If we don't have access token, allow user to add it via CLI
    if ACCESS_TOKEN == None or ACCESS_TOKEN == "" or is_token_valid == False:
        clear()
        printHeader()

        params = prompt(ADD_TOKEN_INTERFACE)

        # User wish to add a token, check for added token's validity.
        if params['add_token'] == True:
            access_token = params['access_token']
            is_token_valid = validateAccessToken(access_token)

            while is_token_valid == False:
                params = prompt(ADD_VALID_TOKEN_INTERFACE)
                retry_add_token = params['retry_add_token']

                if retry_add_token == False:
                    break

                access_token = params['access_token']
                is_token_valid = validateAccessToken(access_token)

            # If the interface gets here either the user had added a valid token
            # or chose to skip and not add instead.
            # Either case, check for validity before writing token to file.
            is_token_valid = validateAccessToken(access_token)

            if is_token_valid:
                writeAccessToken(access_token)
            else:
                writeAccessToken(None)

        else:
            # Else user did not wish to add a token. Write null back to config.json
            writeAccessToken(None)

    params = {}
    params_finalized = False

    while not params_finalized:
        clear()
        printHeader()

        loadAccessToken()
        printGitHubRateLimitStatus()

        INTERFACE[0]['default'] = default_query
        params = prompt(INTERFACE)
        clear()
        printHeader()

        print('\033[39mQuery String: \033[91m' + params['q'])
        print('\033[39mMax Results: \033[91m' + params['max_results'])
        print('\033[39mSort By: \033[91m' + str(params['sort_by']))
        print('\033[39mPrint Logs: \033[91m' + str(params['print_logs']))
        confirm = prompt(CONFIRM_INTERFACE)
        params_finalized = confirm['is_finalized']

    clear()
    printHeader()
    return params

