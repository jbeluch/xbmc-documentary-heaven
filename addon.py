#!/usr/bin/env python
import re
from itertools import chain
from urlparse import urljoin
from xbmcswift import Plugin, download_page, xbmc, xbmcgui
from BeautifulSoup import BeautifulSoup as BS, SoupStrainer as SS
from resources.lib.videohosts import resolve
from resources.lib.googleforms import report_broken_url

__plugin_name__ = 'Documentary Heaven'
__plugin_id__ = 'plugin.video.documentaryheaven'
plugin = Plugin(__plugin_name__, __plugin_id__, __file__)
BASE_URL = 'http://documentaryheaven.com'
ALL_DOCS_URL = 'http://documentaryheaven.com/documentary-list/'


def full_url(path):
    return urljoin(BASE_URL, path)


def htmlify(url):
    return BS(download_page(url))
    

@plugin.route('/')
def show_homepage():
    items = [
        {'label': 'All Documentaries', 'url': plugin.url_for('show_all')},
        {'label': 'By Category', 'url': plugin.url_for('show_categories')},
    ]
    return plugin.add_items(items)


@plugin.route('/all/')
def show_all():
    html = htmlify(ALL_DOCS_URL)
    uls = html.findAll('ul', {'class': 'lcp_catlist'})
    liss = [ul.findAll('li') for ul in uls]

    # Need to extract into tuples first in order to call set(). Cannot call set
    # on dicts since they are mutable.
    label_urls = set((li.a.string, plugin.url_for('play', url=li.a['href']))
                     for li in chain(*liss))
    items = [{'label': label, 
        'url': url, 
        'is_playable': True, 
        'is_folder': False
        } for label, url in label_urls]
    return plugin.add_items(sorted(items, key= lambda item: item['label']))


@plugin.route('/categories/')
def show_categories():
    html = htmlify(BASE_URL)
    categories = html.findAll('li',
                              {'class': lambda cls: cls and 'cat-item' in cls})
    items = [
        {'label': c.a.string,
         'url': plugin.url_for('show_category_videos', category=c.a.string),
        } for c in categories]
    return plugin.add_items(items)

@plugin.route('/categories/<category>/')
def show_category_videos(category):
    html = htmlify(ALL_DOCS_URL)
    categories = html.findAll('div', id='catListItem')
    _category = (div for div in categories if div.h2.string == category).next()
    videos = _category.findAll('li')
    items = [{'label': video.a.string,
              'url': plugin.url_for('play', url=video.a['href']),
              'is_playable': True,
              'is_folder': False,
             } for video in videos]
    return plugin.add_items(sorted(items, key=lambda item: item['label']))


@plugin.route('/play/<url>/')
def play(url):
    plugin_url = resolve(download_page(url))
    if plugin_url:
        return plugin.set_resolved_url(plugin_url)

    # Uh oh, things aren't working. Print the broken url to the log and ask if
    # we can submit the url to a google form.
    current_plugin_url = '?'.join([plugin._argv0, plugin._argv2])
    xbmc.log('REPORT THIS URL: %s' % current_plugin_url)

    dialog = xbmcgui.Dialog()
    user_resp = dialog.yesno('Documentary Heaven Playback Problem.',
                             'There was an issue playing this video.',
                             ('Would you like to report the URL to the'
                              ' developer?'))
    if user_resp:
       report_broken_url(current_plugin_url) 


if __name__ == '__main__': 
    plugin.run()
