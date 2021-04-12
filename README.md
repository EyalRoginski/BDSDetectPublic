# BDSDetect
BDSDetect allows you to look up Pages on Facebook matching a keyword, and measure their engagement in the form of Likes and Follows. While originally written to detect anti-Israeli activity while it is still brewing, it can be used to measure engagement with anything, depending on the keywords.

## How to Download
To download this program, simply download it as a zip from Github, under Code > Download ZIP in the 
repository page.

Alternatively, using the Command Line, while in the target directory, run the following command:

`git clone https://github.com/TheCerealKiller/BDSDetect`

## Requirements
Requires all the packages listed in `requirements.txt` to be installed in the Python environment(currently only selenium). To install the requirements, first download a Python installation from [the website](https://www.python.org/downloads/).

After having installed Python, navigate to the folder using the command line and run the command

`pip install -r requirements.txt`

to install the project requirements.

Also requires a chromedriver.exe file in the same folder as main.py, 
obtainable from [the Chromium website](https://sites.google.com/a/chromium.org/chromedriver/downloads)

## How to Run
In order to run the program, simply run the `main.py` file (while having a Python installation with all the requirements).

Alternatively, you can run the program from the Command Line using:

`python main.py`

To control what keywords are used, simply edit `keywords.csv` before running the program to match the keywords you want to search for.

## Additional Note
After looking up some pages, Facebook doesn't allow us to see any more without logging in, and thus the program skips them. To solve this, try running the program with only some of the keywords (edit the `keywords.csv` file) several times, with gaps of at least a few hours, as the keywords appearing last in the file are usually the ones that suffer the most from lack of access to information.