#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'youngsterxyf'
SITENAME = u'黑 * 白'
SITEURL = 'http://youngsterxyf.github.io'

TIMEZONE = 'Asia/Shanghai'

DEFAULT_LANG = u'zh'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = None
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
LINKS =  (('Pelican', 'http://getpelican.com/'),
          ('explainshell', 'http://www.explainshell.com/'),
          ('BYVoid', 'https://www.byvoid.com/'),
		  ('酷壳', 'http://coolshell.cn/'),
		  ('火丁笔记', 'http://huoding.com/'),
		  ('余果', 'http://yuguo.us/'),
		  ('LaTeX工作室', 'http://www.latexstudio.net/'),
		  ('乱象, 印迹', 'http://www.luanxiang.org/blog/'),
		  ('夏の航海士', 'http://www.soimort.org/'),
		  ('残阳似血', 'http://qinxuye.me/'),
		  ('Right Track Wrong Train', 'http://www.huangz.me/en/latest/index.html'),
		  ('麦子麦', 'http://www.wzxue.com/'),
		  ('Quora', 'http://www.quora.com/'),
		  ('NoOps', 'http://noops.me/'),
		  ('Jia Xiao', 'http://xiao-jia.com/'),
		  ('章炎的主页', 'http://dirlt.com/'),
		  ('High Scalability', 'http://highscalability.com/'),
		  ('Hacker Monthly', 'http://hackermonthly.com/'),
		  ('itkoala', 'http://www.itkoala.com/)(海量运维、运营规划')
		  )

# Social widget
# SOCIAL = (('You can add links in your config file', '#'),
#          ('Another social link', '#'),)

DEFAULT_PAGINATION = 8

THEME = 'my-gum'

DATE_FORMATS = {
	'zh': '%Y-%m-%d %a'
}
RELATIVE_URLS = False

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

GOOGLE_ANALYTICS_ID = 'UA-43488080-1'
GOOGLE_ANALYTICS_SITENAME = u'黑白'

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True
