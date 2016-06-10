#!/usr/bin/env python
# -*- coding: utf-8 -*- #
from __future__ import unicode_literals

AUTHOR = u'youngsterxyf'
SITENAME = u'黑·白'
SITEURL = 'http://youngsterxyf.github.io'

TIMEZONE = 'Asia/Shanghai'

DEFAULT_LANG = u'zh'

# Feed generation is usually not desired when developing
FEED_ALL_ATOM = 'feeds/atom.xml'
FEED_ALL_RSS = 'feeds/rss.xml'
CATEGORY_FEED_ATOM = None
TRANSLATION_FEED_ATOM = None

# Blogroll
# LINKS =  ()

# Social widget
# SOCIAL = (('You can add links in your config file', '#'),
#          ('Another social link', '#'),)

DEFAULT_PAGINATION = 8

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
DISPLAY_PAGES_ON_MENU = False
DISPLAY_CATEGORIES_ON_MENU = False
MENUITEMS = (
    (u'归 档', '/archives.html'),
    (u'工具集', '/pages/tools.html'),
    (u'链 接', '/pages/links.html'),
    (u'技术分享', '/pages/tech-share.html'),
    (u'关于我', '/pages/aboutme.html'),
    (u'RSS', '/feeds/rss.xml')
)

GITHUB_URL = 'http://github.com/youngsterxyf'
TWITTER_URL = 'https://twitter.com/youngsterxyf'
WEIBO_URL = 'http://weibo.com/u/1855563263'
DOUBAN_URL = 'http://www.douban.com/people/youngster21/'
FACEBOOK_URL = ''
GOOGLEPLUS_URL = ''

BAIDU_ANALYTICS_ID = '5c5d8c3fe75afeff117777b9236b96ec'

PLUGIN_PATH = 'plugins'
PLUGINS = ['latex']
LATEX = 'article'

# Uncomment following line if you want document-relative URLs when developing
#RELATIVE_URLS = True

DELETE_OUTPUT_DIRECTORY = True      # 编译之前删除output目录，这样保证output下生成的内容是干净的
