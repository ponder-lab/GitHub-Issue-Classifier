# GitHub-Issue-Mining
Python script to mine for GitHub issues + comments.

### Setup and run instruction:
1) Ensure Python `3.9.1` and corrosponding pip `3.9` are installed
2) Install requirements: `pip3.9 install -r requirements.txt`
3) Run the `main.py` script: `python3.9 main.py`

### Test
1) Ensure that `pytest` is properly set up for your python `3.9` env.
2) Simply run `pytest` to check that all tests are passing.

### TODO:
- ~~Clean comment and properly parse out `<CODE>` blocks in comments~~
- Fix up query to retrieve all result pages (currently only looking at 1 page/100 results)
- Feed data into model to predict comment/lines.
- Set up interface (Web, GUI, CLI?)
