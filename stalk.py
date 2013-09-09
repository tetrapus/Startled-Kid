#!/usr/bin/python2.7
# Reddit data miner

import sys
import re
import time

import requests
import praw

if len(sys.argv) < 2:
	print("Usage: %s user" % sys.argv[0])
	sys.exit(1)

r = praw.Reddit(user_agent='startled-kid/0.0.1 via praw by Lyucit')

user = r.get_redditor(sys.argv[1])

print "---- User Data ----"
print "%s (%s)%s%s%s%s" % (user.name, user.fullname, 
					   " [GOLD]" if user.is_gold else "", 
					   " [MOD]" if user.is_mod else "", 
					   " [VERIFIED]" if user.has_verified_email else "",
					   " [CHILD]" if not user.over_18 else "")
print "Created :      %s UTC" % time.asctime(time.gmtime(user.created_utc))

print "Fetching submission history..."
submissions = list(user.get_submitted(limit=None))

if submissions:
	print "---- Link Data ----"
	print "Most upvotes: %s" % max(submissions, key=lambda x: x.ups)
	print "Most downvotes: %s" % max(submissions, key=lambda x: x.downs)
	print "Best: %s" % max(submissions, key=lambda x: x.score)
	print "Worst: %s" % min(submissions, key=lambda x: x.score)
	print "Links: %s" % len(submissions)
	print "Link karma: %d (%.2fpts/day, %.2fpts/post)"    % (user.link_karma,86400* user.link_karma / (time.time() - user.created_utc), user.link_karma / len(submissions) if submissions else 0)

print "Fetching comment history..."
comments = list(user.get_comments(limit=None))

if comments:
	print "---- Comment Data ----"
	print "Most upvotes: %s" % max(comments, key=lambda x: x.ups)
	print "Most downvotes: %s" % max(comments, key=lambda x: x.downs)
	print "Best: %s" % max(comments, key=lambda x: x.score)
	print "Worst: %s" % min(comments, key=lambda x: x.score)
	print "Comments: %s" % len(comments)
	print "Comment karma: %d (%.2fpts/day, %.2fpts/comment)" % (user.comment_karma,86400*user.comment_karma / (time.time() - user.created_utc), user.comment_karma / len(comments) if submissions else 0)

csubs = [i.subreddit.display_name for i in comments]
ssubs = [i.subreddit.display_name for i in submissions]
subreddits = csubs + ssubs


gonewild = open("data/gonewild.txt").read().split()
gonemild = open("data/gonemild.txt").read().split()

def is_gw_sub(subname):
	sub = subname.lower()
	if sub in gonewild:
		return True
	elif sub.endswith("gw") or "gonewild" in sub:
		print "Warning: heuristic detected subreddit not in list. Please report to the developer."
		print "Click here: http://www.reddit.com/message/compose/?to=Lyucit&subject=Missing%20gw%20subreddit%20entry&message=" + sub + "%20is%20missing%20from%20your%20subreddit%20list."
		return True
	return False

def is_gm_sub(subname):
	sub = subname.lower()
	if sub in gonemild:
		return True
	elif sub.endswith("gm") or "gonemild" in sub:
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

# Generate a statistical analysis
print "---- Subreddit breakdown ----"
print "Total | Post | Reply | Subreddit"
breakdown = set(subreddits)
breakdown = [(subreddits.count(i), ssubs.count(i), csubs.count(i), i) for i in breakdown]
breakdown.sort(key=lambda x: (-x[0], -x[1], -x[2], x[3]))
for i in breakdown:
	print "%5d  %5d   %5d   /r/%s" % i

words = sum(len(i.body.split()) for i in comments)
letters = sum(len(i.body) for i in comments)
dictionary = set(open("/usr/share/dict/words").read().lower().split())

reduce_words = " ".join([i.body for i in comments]) # Join comments
reduce_words = re.sub(r"((([A-Za-z]{3,9}:(?:\/\/)?)(?:[-;:&=\+\$,\w]+@)?[-A-Za-z0-9.]+|(?:www.|[-;:&=\+\$,\w]+@)[-A-Za-z0-9.]+)((?:\/[-\+~%\/.\w_]*)?\??(?:[-\+=&;%@.\w_]*)#?(?:[\w]*))?)", " ", reduce_words)
reduce_words = re.sub(r"&.{1,6};", " ", reduce_words)
reduce_words = re.sub(r"([^-'\w]|_)", " ", reduce_words)
reduce_words = re.sub(r"(([^\w])[-']|[-']([^\w])|^[-']|[-']$)", " ", reduce_words).lower().split()
reduce_words = [i for i in reduce_words if not re.match(r"\d", i) and re.match("[a-zA-Z]", i)]
uninteresting = set(open("data/uninterestingwords.txt").read().lower().split())
unique = set(reduce_words) - dictionary - uninteresting

if comments:
	print "---- Word Data ----"
	print "Letters used: %s" % letters
	print "Words: %s" % words
	print "Unique words: %s" % len(set(reduce_words))
	print "Non-dictionary words: %s (%2f%%)" % (len(unique), 100*len(unique)/len(reduce_words))
	print "Most common: %s" % (", ".join(sorted(list(unique), key=lambda x: -reduce_words.count(x))[:10])) 
	print "Words/comment: %s" % (float(words) / len(comments))
	print "Karma/Letter: %s" % (float(user.comment_karma) / letters)
	print "Karma/Word: %s"% (float(user.comment_karma) / words)


narcissist = [re.findall(r"([^.\n[]]*\bi('m a| am a| live| have| used to| go to| love| use| work at)\b[^.\n\[\]]+)", i.body, flags=re.IGNORECASE) for i in comments]
narcissist += [re.findall(r"([^.\n[]]*\bi('m a| am a| live| have| used to| go to| love| use| work at)\b[^.\n\[\]]+)", i.selftext, flags=re.IGNORECASE) for i in submissions if i.is_self]
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
		# temporary fix
		print "%s (%s | %s up, %s down)" % (i.title, i.subreddit.url, i.ups, i.downs)
		print "%s%s" % (i.url, " [NSFW]" if i.over_18 else "")

cities = open("data/cities.txt").read().split()
countries = open("data/countries.txt").read().split()

city = [i for i in subreddits if i.lower() in cities]
if not cities:
	city = [i for i in subreddits if i.lower() in countries]
if city:
	best = max(city, key=city.count)
	print "** Probably lives in %s (confidence = %3f)" % (best, float(city.count(best)) / len(city))

dsubs = set(open("data/drugs.txt").read().split()) & ({i.lower() for i in ssubs} | {i.lower() for i in csubs})
lowersubs = map(unicode.lower, subreddits)
dsubs = [(i, lowersubs.count(i)) for i in dsubs]
if dsubs:
	print "Probably a drug user. Contributor to: %s" % (", ".join("%s[%d]" % i for i in sorted(dsubs, key=lambda x: -x[1])))

uflairs = set(open("data/flairreddits.txt").read().split())
fsubs = uflairs & ({i.lower() for i in ssubs} | {i.lower() for i in csubs})
if "-f" in sys.argv:
	fsubs |= {i.lower() for i in ssubs} | {i.lower() for i in csubs}


print "Requesting flair data on %d subreddits..." % len(fsubs)
flairs = {}
firstflair = True
for i in fsubs:
	flair = r.get_flair(i, sys.argv[1])
	flairtext = flair["flair_text"].encode('utf-8')
	if flair["flair_css_class"]:
		flairtext = "%s: %s" % (flair["flair_css_class"].encode("utf-8"), flairtext)
	if flairtext:
		if firstflair:
			print "---- Known Flair ----"
		firstflair = False
		flairs.update({i: flair})
		print "%sr/%s - %s" % ("*" if i.lower() not in uflairs else "", i, flairtext)

if "EDC" in ssubs:
	print "Found EDC post(s):"
	for i in submissions:
		if i.subreddit.display_name == "EDC":
			print i
name = []
age = []
gender = []
country = []
# Guess external profiles
okcupid = requests.get("http://okcupid.com/profile/%s" % sys.argv[1]).text
if "<title>OkCupid |  Account not found</title>" not in okcupid:
	print "Possible OkCupid found: http://okcupid.com/profile/%s" % sys.argv[1]
	okcdata = re.findall("<title>(.*?)</title>", okcupid)
	if okcdata: print okcdata[0]
github = requests.get("http://github.com/%s" % sys.argv[1]).text
if "<title>Page not found &middot; GitHub</title>" not in github:
	print "Possible github found: http://github.com/%s" % sys.argv[1]
	ghdata = re.findall("<title>(.*?)</title>", github)[0]
	print ghdata
	ghndata = re.findall("\((.*)\)", ghdata)
	if ghndata:
		name.append(ghndata)

twitter = requests.get("http://twitter.com/%s" % sys.argv[1]).text
if "<title>Twitter / ?</title>" not in twitter:
	print "Possible twitter found: http://twitter.com/%s" % sys.argv[1]
	twtdata = re.findall("<title>(.*?)</title>", twitter)
	if twtdata:
		twtdata = twtdata[0]
		twtname = re.findall("^(.+) \(", twtdata)
		if twtname:
			print twtname[0]
			name.append(twtname[0])
		else:
			print twtdata

imgur = requests.get("http://imgur.com/user/%s" % sys.argv[1]).text
if "<title>	imgur: the simple 404 page</title>" not in imgur:
	print "Possible imgur found: http://%s.imgur.com/" % sys.argv[1]
	print "             Gallery: http://imgur.com/user/%s" % sys.argv[1]

lastfm = requests.get("http://www.last.fm/user/%s" % sys.argv[1]).text
if "<title>Last.fm - Listen to internet radio and the largest music catalogue online</title>" not in lastfm:
	print "Possible last.fm found: http://www.last.fm/user/%s" % sys.argv[1]
	lfmdata = re.findall('<p class="userInfo adr">.*?</p>', lastfm)
	if lfmdata:
		# print re.sub("<.*?>", "\n", lfmdata[0])
		userdata = re.findall('<strong class="fn">(.*?)</strong>(?:, (\d+))?(?:, (Male|Female))?(?:, <span class="country-name">(.*?))?<', lfmdata[0])
		if userdata:
			userdata = userdata[0]
			print userdata
			name.append(userdata[0])
			age.append(userdata[1])
			gender.append(userdata[2])
			country.append(userdata[3])
		else:
			print re.sub("<.*?>", "\n", lfmdata[0]).strip().replace("\n\n", "|").replace("\n", " ")

facebook = requests.get("http://facebook.com/%s" % sys.argv[1]).text
if '<title id="pageTitle">Page Not Found | Facebook</title>' not in facebook:
	if '<title id="pageTitle">Content Not Found | Facebook</title>' not in facebook:

		print "Possible public facebook profile found: http://facebook.com/%s" % sys.argv[1]
		fbname = re.findall(r">(.*?) \| Facebook<", facebook)
		if fbname:
			print fbname
			name.append(fbname)
	else:
		print "Probably has private facebook profile"

tumblr = requests.get("http://%s.tumblr.com/" % sys.argv[1]).text
if "<title>Not found.</title>" not in tumblr:
	print "Possible tumblr profile: http://%s.tumblr.com/" % sys.argv[1]

class Profile(object):
	"""
	Build a profile of known data for a user.
	"""
	age = []
	sex = []
	sexuality = []
	phone = []
	city = []
	country = []
	drugs = []
	mbti = []
	politics = []
	religion = []
	social = []
	hipster = [] # subreddits like mfa, coffee, etc
	depression = []

class Metric(object):
	pass

class FlairData(Metric):
	pass

