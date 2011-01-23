"""
Provides wordlists to the application.  Each wordlist is a text file
stored in the module directory, with one word or phrase per line.  The
module exposes these wordslists to the application as sets of strings.

The dynamic creation of the module attributes relies on a trick
described at http://stackoverflow.com/questions/2933470
"""

from glob import iglob
import os

__all__ = []
MODULE_PATH = os.path.abspath(os.path.dirname(__file__))

# The del statements clean up variables so that they're not accessible
# after the module loads.

for wordlist_path in iglob(MODULE_PATH + '/*.txt'):
    name = os.path.splitext(os.path.split(wordlist_path)[1])[0]
    wordlist = set()
    with open(wordlist_path) as wordlist_file:
        for line in wordlist_file:
            wordlist.add(line.strip())
            del line
    __all__.append(name)
    globals()[name] = wordlist
    del wordlist_file
    del wordlist_path
    del wordlist
    del name
del MODULE_PATH
