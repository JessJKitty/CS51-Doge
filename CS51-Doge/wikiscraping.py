import bs4
import urllib2

def wikiscraping (word):

    url_att = 'https://en.wikipedia.org/wiki/' + word

    response = urllib2.urlopen(url_att)
    soup = bs4.BeautifulSoup(response.read())
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
    def notmain(atag): return not(atag.get('href', '').startswith('/wiki/Main_Page'))
    not_main = filter(notmain, no_metas)


    # take the titles from the hrefs. 
    def striptitle(atag): return atag.get('title', '')
    titles = map(striptitle, not_main)

    #if the page does not exist return empty. 
    if titles == ['Case sensitivity']:
        return []
    else:
        #else return all the titles
        return titles

