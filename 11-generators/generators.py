#!/usr/bin/env python3
"""
Turn the following unix pipeline into Python code using generators

$ for i in ../*/*py; do grep ^import $i|sed 's/import //g' ; done | sort | uniq -c | sort -nr

      8 os
      7 csv
      6 sys
      5 re
      4 unittest
      4 tweepy
      3 random
      3 json
      2 time
      2 sqlite3
      2 itertools
      1 xml.etree.ElementTree as ET
      1 time, itertools
      1 textwrap, random
      1 requests  # call Marvel API
      1 requests
      1 random, itertools, sys, shelve, getpass
      1 json  # use dumps and loads
      1 import_regex = re.compile('^(?:from|import)\s(?P<module>\w+).*')
      1 hashlib  # needed for API auth
      1 glob
      1 feedparser
      1 difflib
"""
from pathlib import Path
import re
from collections import Counter

PATTERN = r'^import (\w+)'


def gen_files(pat):
    # Each call returns a new file handler
    for filename in Path('.').glob(pat):
        yield open(filename, 'rt')


def gen_lines(files):
    # Return get lines of text from each file in files
    for file in files:
        yield from file


def gen_grep(lines, pattern):
    # Does a bit more than grep
    regex = re.compile(pattern)
    return (line.replace("import ", "").rstrip("\n") for line in lines
            if regex.search(line))


def gen_count(lines):
    yield from Counter(lines).most_common()


if __name__ == "__main__":
    # call the generators, passing one to the other
    files = gen_files('../*/*.py')
    # print([f for f in file])
    lines = gen_lines(files)
    import_packages = gen_grep(lines, PATTERN)

    for x in gen_count(import_packages):
        print("{:>2} {}".format(x[1], x[0]))
