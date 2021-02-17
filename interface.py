from pyfiglet import Figlet
from PyInquirer import prompt
from prompt_toolkit.validation import Validator, ValidationError
from utils.io import clear
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
    # TODO: Need to figure out how to deal with query limit.
    # {
    #     'type': 'input',
    #     'name': 'top_n_results',
    #     'message': "Filter top N results (3 by default/1000 max):",
    #     'validate': MaxResultValidator
    # },
    {
        'type': 'list',
        'name': 'sort_by',
        'message': "Sort by:",
        'choices': ['Best Match', 'Comments'],
        'filter': lambda val: SORT_OPTIONS_MAP[val]
    },
    {
        'type': 'checkbox',
        'name': 'omitted_classes',
        'message': "Omit classification categories:",
        'choices': [
            { 'name': 'Expected Behaviour'},
            { 'name': 'Motivation'},
            { 'name': 'Observed Bug Behaviour'},
            { 'name': 'Bug Reproduction'},
            { 'name': 'Investigation and Exploration'},
            { 'name': 'Solution Discussion'},
            { 'name': 'Contribution and Commitment'},
            { 'name': 'Task Progress'},
            { 'name': 'Testing'},
            { 'name': 'Future Plan'},
            { 'name': 'New Issues and Requests'},
            { 'name': 'Solution Usages'},
            { 'name': 'WorkArounds'},
            { 'name': 'Issue Content Management'},
            { 'name': 'Action on Issue'},
            { 'name': 'Social Conversation'}
        ],
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

# Print CLI header
def printHeader():
    f = Figlet(font='big')
    print(f.renderText('GitHub Issue Classifier'))
    print('GitHub Issue Classifier CLI Tool')
    print('PONDER Lab - https://github.com/ponder-lab \n')

# Main Interface Function
def InitializeSearchInterface():
    params = {}
    params_finalized = False

    while not params_finalized:
        clear()
        printHeader()

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

# Dev mode, call function below to load the interface
# returnedParams = InitializeSearchInterface()
# print(returnedParams)