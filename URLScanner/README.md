# URL Scanner
## Purpose
At first, i've made that project to learn the basics of python, using simple stuff such as a GET request on a URL to get its HTML content.

One thing leading to another, i've decided to extract all of the URLs within the website (not the external one) by scanning all the links.

In order to speed this process up, i've tried to use the ThreadPoolExecutor in order to play with Thread and Mutex with Python.

I've also found that i could use type checking on variables, which i think is cool, so i've used that on some part of the code to test this feature of Python.

NB : I have only run that project on Windows. I assume it could work on a Unix system with some minor adjustments (replacing '\\' by '/' for example).

## How to use it
Simply run it like this on a command line where Python is already in %PATH% :
$> python main.py https://mywebsitetoscan.com

To add some debug strings in the logs :
$> python main.py --debug https://mywebsitetoscan.com
