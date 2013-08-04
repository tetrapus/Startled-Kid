#!/usr/bin/python2.7
# Reddit data miner

import sys

import praw

if len(sys.argv) != 2:
	print("Usage: %s user" % sys.argv[0])
	sys.exit(1)

r = praw.Reddit(user_agent='startled-kid/0.0.1 by Lyucit')

user = r.get_redditor(sys.argv[1])

print "Fetching comment history..."
comments = list(user.get_comments(limit=None))
print "Fetching submission history..."
submissions = list(user.get_submitted(limit=None))
likes = []
dislikes = []
subreddits = []
friends = []

csubs = [i.subreddit.display_name for i in comments]
ssubs = [i.subreddit.display_name for i in submissions]
#print csubs
#print ssubs

gonewild = open("data/gonewild.txt").read().split()

def is_gw_sub(subname):
	sub = subname.lower()
	if sub in gonewild:
		return True
	elif "gw" in sub or "gonewild" in sub:
		print "Warning: heuristic detected subreddit not in list. Please report to developer."
		print "Click here: http://www.reddit.com/message/compose/?to=Lyucit&subject=Missing%20gw%20subreddit%20entry&message=" + sub + "%20is%20missing%20from%20your%20subreddit%20list."
		return True
	return False

def get_gonewild(posts):
	posts = [i for i in posts if is_gw_sub(i.subreddit.display_name)]
	return posts

for i in get_gonewild(submissions):
	print "%s (%s | %s up, %s down)" % (i.title, i.subreddit.url, i.ups, i.downs)
	print "%s%s" % (i.url, " [NSFW]" if i.over_18 else "")