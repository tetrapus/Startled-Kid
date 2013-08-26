#!/usr/bin/env python
"""
Perform a bfs on a subreddit's sidebar.

Usage: 
    %(name)s <subreddit> [options]
    %(name)s -h

Options:
    -m, --max N        Exit after discovering N subreddits. Note this does not
                       imply the output will have N entries, only that it will 
                       not request more after it has discovered the first N.
    -d, --depth N      Exit after traversing all subreddits within N degrees of 
                       separation from the first
    -o, --output FILE  Write output to FILE instead of stdout 
    -t, --tree         Structure output as a tree. This flag changes the search
                       mode to depth-first search.
    -h, --help         Show this help message and exit
"""

# TODO: live output

import sys
from collections import deque
import re

import praw
from docopt import docopt

class Subreddit(object):
    """
    Tracks a subreddit's position in the graph
    """
    def __init__(self, sub, parent=None):
        self.subreddit = None
        self.name = sub.lower()
        self.full_name = sub
        self.parent = parent
        if parent:
            self.parent.addchild(self)
            self.level = parent.level + 1
        else:
            self.level = 0
        self.children = []

    def refs(self):
        if self.subreddit is None:
            self.subreddit = r.get_subreddit(self.name)

        return re.findall(r"/r/([A-Za-z0-9]\w{2,20}|[a-z]{2})", self.subreddit.description)

    def addchild(self, child):
        self.children.append(child)

    def __str__(self):
        if args["--tree"]:
            return ("   " * self.level) + self.full_name
        else:
            return self.full_name



# Handle arguments
args = docopt(__doc__ % {"name": sys.argv[0]})

def checkskip(current):
    if args["--max"] is not None and int(args["--max"]) < len(sub_visited):
        return True
    if args["--depth"] is not None and int(args["--depth"]) <= current.level:
        return True
    return False

def popnext(queue):
    if args["--tree"]:
        sub = queue.pop()
    else:
        sub = queue.popleft()
    return sub

if args["--output"]:
    sys.stdout = open(args["--output"], "w")

# Initialise reddit session
r = praw.Reddit(user_agent='startled-kid/0.0.1 via praw by Lyucit')

sub_visited = [Subreddit(args["<subreddit>"])]
sub_queue = deque(sub_visited)

try:
    while sub_queue:
        sub = popnext(sub_queue)
        print sub

        if checkskip(sub):
            continue

        for i in sub.refs():
            if i.lower() not in [x.name for x in sub_visited]:
                next = Subreddit(i, sub)
                sub_visited.append(next)
                sub_queue.append(next)

except KeyboardInterrupt:
    for i in sub_queue:
        print i