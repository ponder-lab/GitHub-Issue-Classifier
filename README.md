# GitHub-Issue-Mining
[![Build Status](https://www.travis-ci.com/ponder-lab/GitHub-Issue-Mining.svg?token=hsn7ZoyjgYPPHKxyfxk7&branch=main)](https://www.travis-ci.com/ponder-lab/GitHub-Issue-Mining)

Python script to mine for GitHub issues + comments and classify them.

![CLI Tool Screenshot](./cli_screenshot.png)

### Setup and run instruction:
1) Ensure Python `3.9.1` and corrosponding pip `3.9` are installed
2) Install requirements: `pip3.9 install -r requirements.txt`
3) Run the `main.py` script: `python3.9 main.py` to start up the interface.

### Test
1) Ensure that `pytest` is properly set up for your python `3.9` env.
2) Simply run `pytest` to check that all tests are passing.

### Folder Structure
`/src` - Contains the main driver file used for running the script/querying API and classification, along with the CLI interface

`/utils` - Contains utility function files, such as IO, filtering results and processing comments

`/test` - Contains test file being ran by `pytest`

`/result` - Folder to output result files to. Contains a `.gitignore` to ignore all files in this folder to prevent results from being committed