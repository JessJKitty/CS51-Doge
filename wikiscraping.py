from __future__ import print_function
import requests
import bs4


response = requests.get('https://en.wikipedia.org/wiki/Doge_(meme)')
soup = bs4.BeautifulSoup(response.text)
links = soup.find_all('a')

# excludes external links
def isinternal(atag): return atag.get('href', '').startswith('/wiki/')
internal_links = filter(isinternal, links)

# excludes images
def notimage(atag): return atag.img is None
no_images = filter(notimage, internal_links)

# excludes Citation Needed links
def notspan(atag): return atag.span is None
no_wikimedia = filter(notspan, no_images)

# excludes Portal: Content, Help: Images, etc.
def notspecial(atag): return not ':' in atag.get('href', '')
no_specials = filter(notspecial, no_wikimedia)

# excludes View the Content, View Talk Page
def notmeta(atag): return atag.get('accesskey', None) is None
no_metas = filter(notmeta, no_specials)

# not the main page
def notmain(atag): return atag.get('href', '').startswith('/wiki/Main_Page')
not_main = filter(notmain, no_metas)

# take the titles from the hrefs. 
def striptitle(atag): return atag.get('title', '')
titles = map(striptitle, not_main)

for x in titles:
    print (x)
