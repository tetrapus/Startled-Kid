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

csubs = [i.subreddit.display_name for i in comments]
ssubs = [i.subreddit.display_name for i in submissions]
subreddits = csubs + ssubs


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
	posts = [i for i in posts if is_gw_sub(i.subreddit.display_name) or i.over_18 and re.search("[[({<][mft]+[]})>]", i.title, flags=re.IGNORECASE)]
	return posts

def get_gonemild(posts):
	posts = [i for i in posts if is_gm_sub(i.subreddit.display_name)]
	return posts

def get_selfies(posts):
	# Currently only detects me mondays
	posts = [(i, re.findall(r"\[.*\]\((.+)\)", i.body)) for i in posts]
	links = []
	for post, urls in posts:
		urls = [i for i in urls if not i.endswith(".gif")]
		#if urls and "me monday" in post.submission.title.lower():
		for url in urls:
			links.append((post, url))

	return links


def get_nsfw_submissions(posts, include_gw=False):
	posts = [i for i in posts if i.over_18 and not i.is_self]
	if not include_gw:
		posts = [i for i in posts if not is_gw_sub(i.subreddit.display_name)]
	return posts

narcissist = [re.findall(r"([^.\n[]]*\bi('m a| am a| live| have| used to| go to| love| use)\b[^.\n\[\]]+)", i.body, flags=re.IGNORECASE) for i in comments]
narcissist += [re.findall(r"([^.\n[]]*\bi('m a| am a| live| have| used to| go to| love| use)\b[^.\n\[\]]+)", i.selftext, flags=re.IGNORECASE) for i in submissions if i.is_self]
narcissist = [i[0][0] for i in narcissist if i]
narcissist = [i for i in narcissist if "than i " not in i.lower() and "i have no" not in i.lower() and "i have gotten" not in i.lower()] # be conservative
if narcissist:
	print "---- About ----"
	for i in narcissist:
		print i

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
#selfies = get_selfies(comments)
#if selfies:
#	print "---- Comment links ----"
#	for i, url in selfies:
#		print "%s (%s | %s up, %s down)" % (url, i.subreddit.url, i.ups, i.downs)

nsfw = get_nsfw_submissions(submissions)
if nsfw:
	print "---- NSFW Submissions ----"
	for i in nsfw:
		print "%s (%s | %s up, %s down)" % (i.title, i.subreddit.url, i.ups, i.downs)
		print "%s%s" % (i.url, " [NSFW]" if i.over_18 else "")

subreddits = set(open("data/flairreddits.txt").read().split()) & ({i.lower() for i in ssubs} | {i.lower() for i in csubs})
if "-f" in sys.argv:
	subreddits |= {i.lower() for i in ssubs} | {i.lower() for i in csubs}

cities = open("data/cities.txt").read().split()
countries = open("data/countries.txt").read().split()

city = [i for i in subreddits if i.lower() in cities]
if not cities:
	city = [i for i in subreddits if i.lower() in countries]
if city:
	best = max(city, key=city.count)
	print "** Probably lives in %s (confidence = %d)" % (best, float(city.count(best)) / len(cities))


firstflair = True
for i in subreddits:
	flair = r.get_flair(i, sys.argv[1])
	flairtext = flair["flair_text"]
	if flair["flair_css_class"]:
		flairtext = "%s: %s" % (flair["flair_css_class"], flairtext)
	if flairtext:
		if firstflair:
			print "---- Known Flair ----"
		firstflair = False
		print "r/%s - %s" % (i, flairtext)

class Profile(object):
	"""
	Build a profile of known data for a user.
	"""
	age = None
	sex = None
	sexuality = None
	phone = None
	city = None
	country = None
	drugs = None
	mbti = None
	politics = None
	religion = None
	social = None
	hipster = None # subreddits like mfa, coffee, etc
	depression = None

class Metric(object):
	pass