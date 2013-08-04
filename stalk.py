#!/usr/bin/python2.7
# Reddit data miner

import sys
import re

import praw

if len(sys.argv) < 2:
	print("Usage: %s user" % sys.argv[0])
	sys.exit(1)

r = praw.Reddit(user_agent='startled-kid/0.0.1 via praw by Lyucit')

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
gonemild = open("data/gonemild.txt").read().split()

def is_gw_sub(subname):
	sub = subname.lower()
	if sub in gonewild:
		return True
	elif "gw" in sub or "gonewild" in sub:
		print "Warning: heuristic detected subreddit not in list. Please report to the developer."
		print "Click here: http://www.reddit.com/message/compose/?to=Lyucit&subject=Missing%20gw%20subreddit%20entry&message=" + sub + "%20is%20missing%20from%20your%20subreddit%20list."
		return True
	return False

def is_gm_sub(subname):
	sub = subname.lower()
	if sub in gonemild:
		return True
	elif "gm" in sub or "gonemild" in sub:
		print "Warning: heuristic detected subreddit not in list. Please report to the developer."
		print "Click here: http://www.reddit.com/message/compose/?to=Lyucit&subject=Missing%20gm%20subreddit%20entry&message=" + sub + "%20is%20missing%20from%20your%20subreddit%20list."
		return True
	return False

def get_gonewild(posts):
	posts = [i for i in posts if is_gw_sub(i.subreddit.display_name)]
	return posts

def get_gonemild(posts):
	posts = [i for i in posts if is_gm_sub(i.subreddit.display_name)]
	return posts

def get_nsfw_submissions(posts, include_gw=False):
	posts = [i for i in posts if i.over_18 and not i.is_self]
	if not include_gw:
		posts = [i for i in posts if not is_gw_sub(i.subreddit.display_name)]
	return posts

gw = get_gonewild(submissions)
if gw:
	print "---- Gonewild Submissions ----"
	for i in gw:
		print "%s (%s | %s up, %s down)" % (i.title, i.subreddit.url, i.ups, i.downs)
		print "%s%s" % (i.url, " [NSFW]" if i.over_18 else "")
gm = get_gonemild(submissions)
if gm:
	print "---- Gonemild Submissions ----"
	for i in gm:
		print "%s (%s | %s up, %s down)" % (i.title, i.subreddit.url, i.ups, i.downs)
		print "%s%s" % (i.url, " [NSFW]" if i.over_18 else "")
nsfw = get_nsfw_submissions(submissions)
if nsfw:
	print "---- NSFW Submissions ----"
	for i in nsfw:
		print "%s (%s | %s up, %s down)" % (i.title, i.subreddit.url, i.ups, i.downs)
		print "%s%s" % (i.url, " [NSFW]" if i.over_18 else "")
narcissist = [re.findall(r"(\bi( am a| live| have)\b[^.]+\.)", i.body, flags=re.IGNORECASE) for i in comments]
narcissist = [i[0][0] for i in narcissist if i]
if narcissist:
	print "---- About ----"
	for i in narcissist:
		print i

subreddits = set(open("data/flairreddits.txt").read().split()) & ({i.lower() for i in ssubs} | {i.lower() for i in csubs})
if "-f" in sys.argv:
	subreddits |= {i.lower() for i in ssubs} | {i.lower() for i in csubs}

flairs = {i:r.get_flair(i, sys.argv[1])["flair_text"] for i in subreddits}
flairs = {k:v for k, v in flairs.items() if v}
if flairs:
	print "---- Known Flair ----"
	for k, v in flairs.items():
		print "r/%s - %s" % (k, v)

cities = open("data/cities.txt").read().split()

city = [i for i in csubs + ssubs if i.lower() in cities]
if city:
	print "Probably lives in %s" % max(city, key=city.count)


