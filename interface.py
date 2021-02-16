from pyfiglet import Figlet
from PyInquirer import prompt
from os import system, name
from prompt_toolkit.validation import Validator, ValidationError
import regex

# Params validator
class QueryStringValidator(Validator):
    def validate(self, document):
        if not document.text.replace(' ', ''):
            raise ValidationError(
                message='Please enter a search string to query',
                cursor_position=0)

class MaxResultValidator(Validator):
    def validate(self, document):
        ok = regex.match('^([1-9]|[1-9][0-9]|[1-9][0-9][0-9])$', document.text)
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
        'validate': QueryStringValidator
    },
    {
        'type': 'input',
        'name': 'max_results',
        'message': "Max number of results (1000 max/default):",
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

# Screen Clear
def clear():

    # for windows
    if name == 'nt':
        _ = system('cls')

        # for mac and linux(here, os.name is 'posix')
    else:
        _ = system('clear')

def printHeader():
    f = Figlet(font='big')
    print(f.renderText('GitHub Issue Classifier'))
    print('GitHub Issue Classifier')
    print('PONDER Labs - https://github.com/ponder-lab \n')

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

