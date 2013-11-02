#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'youngsterxyf'
SITENAME = u'黑 * 白'
SITEURL = 'http://youngsterxyf.github.io/newblog'

TIMEZONE = 'Asia/Shanghai'

DEFAULT_LANG = u'zh'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS =  (('Pelican', 'http://getpelican.com/'),
          ('explainshell', 'http://www.explainshell.com/'),)

# Social widget
SOCIAL = (('You can add links in your config file', '#'),
          ('Another social link', '#'),)

DEFAULT_PAGINATION = 10

THEME = 'my-gum'

DATE_FORMATS = {
	'zh': '%Y-%m-%d %a'
}
RELATIVE_URLS = True

DISQUS_SITENAME = "xiayfblackwhite"

#ARTICLE_DIR = 'posts'
ARTICLE_URL = '{date:%Y}/{date:%m}/{date:%d}/{slug}/'
ARTICLE_SAVE_AS = '{date:%Y}/{date:%m}/{date:%d}/{slug}/index.html'

DEFAULT_CATEGORY = u'其他'

PAGE_DIR = 'pages'
PAGE_URL = 'pages/{slug}.html'
PAGE_SAVE_AS = 'pages/{slug}.html'
DISPLAY_PAGES_ON_MENU = True

GITHUB_URL = 'http://github.com/youngsterxyf'
TWITTER_URL = 'https://twitter.com/youngsterxyf'
WEIBO_URL = 'http://weibo.com/u/1855563263'
DOUBAN_URL = 'http://www.douban.com/people/youngster21/'
FACEBOOK_URL = ''
GOOGLEPLUS_URL = ''

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
