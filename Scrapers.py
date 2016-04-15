import requests
from bs4 import BeautifulSoup
import re
import json

class NYT_Scraper:
    '''Scrapes The New York Times Website and formats text, links, etc.
    '''

    def __init__(self, url):
        self.html = requests.get(url).text
        self.soup = BeautifulSoup(self.html)
        self.SOURCE = 'The New York Times'


    def format_date(self, date):
        date = str(date)
        return '{}/{}/{}'.format(date[4:6], date[6:8], date[0:4])


    def get_authors(self):

        def capitalize(name):
            items = name.split()
            items = [x[0].upper() + x[1:].lower() for x in items]
            return ' '.join(items)

        authors = self.soup.find('meta', {'name': 'author'})['content']
        return capitalize(authors)\
            .replace(' And ', '; ')\
            .replace(' and ', '; ')\
            .replace(',', '; ')


    def get_date_published(self):
        return self.format_date(self.soup.find('meta', {'name': 'pdate'})['content'])


    def get_title(self):
        return self.soup.find('meta', {'name': 'hdl'})['content'].encode('utf-8')


    def get_tweets(self, html):

        remove_doubles = lambda x: list(set(x))

        tweet_ids = re.findall('twitter.com/.*/statuses/(\d+)', html) + \
                    re.findall('twitter.com/.*/status/(\d+)', html)
        # removes duplicates
        tweets = remove_doubles(['[tweetbegin {} tweetend]'.format(tweet_id)
                                for tweet_id in tweet_ids])
        return tweets


    def get_text(self):
        '''Takes in a NYT url and spits out the raw text
        '''

        out_text = []

        for paragraph in self.soup.findAll('p', {'class': 'story-body-text'}):
            text = paragraph.text
            if paragraph.findChildren() != []:
                replacement_links = []
                for link in paragraph.findChildren():
                    if link.contents:
                        contents = unicode(link.contents[0])
                    else:
                        contents = ''
                    if link.get('href'):
                        href = link.get('href')
                        formatted_href =\
                            '{' + contents + '}<hyperlink="' + href + '">'
                        replacement_links.append((contents, formatted_href))
                for link in replacement_links:
                    text = text.replace(link[0], link[1], 1)
            out_text.append(text)

        tweets = self.get_tweets(self.html)

        return out_text + tweets


    def dump_all(self):
        output = {
            'source': self.SOURCE.decode('utf-8'),
            'published': self.get_date_published().decode('utf-8'),
            'authors': self.get_authors().decode('utf-8'),
            'title': self.get_title().decode('utf-8'),
            'text': [unicode(x) for x in self.get_text()]
        }

        return output

class CBSNews_Scraper:
    '''Scrapes and parses CBS News text
       Converts Links to the following format
       {click me}<hyperlink="http://www.gohere.com">
    '''

    def format_href(self, contents, href):
        return '{' + contents + '}<hyperlink="' + href + '">'

    def __init__(self, url):
        self.html = requests.get(url).text
        self.soup = BeautifulSoup(self.html)
        self.SOURCE = 'CBS News'
        self.json = json.loads(self.soup.find('body')['data-tracking'])


    def get_authors(self):

        def capitalize(name):
            items = name.split()
            items = [x[0].upper() + x[1:].lower() for x in items]
            return ' '.join(items)

        authors = '; '.join(self.json['articleAuthorName'])
        return capitalize(authors)


    def get_date_published(self):
        '''Date is in this format 2016-02-23 19:05:17'''
        date_string = self.json['articlePubDate'][:10]
        return '{}/{}/{}'.format(date_string[5:7], date_string[8:], date_string[:4])


    def get_title(self):
        return self.soup.find('meta', {'property': 'og:title'})['content'].encode('utf-8')


    def get_tweets(self, html):

        remove_doubles = lambda x: list(set(x))

        tweet_ids = re.findall('twitter.com/.*/statuses/(\d+)', html) + \
                    re.findall('twitter.com/.*/status/(\d+)', html)
        # removes duplicates
        tweets = remove_doubles(['[tweetbegin {} tweetend]'.format(tweet_id)
                            for tweet_id in tweet_ids])
        return tweets

    def get_text(self):
        '''
        Takes in a url and spits out the raw text
        '''
        body_paras = self.soup.find('div', {'itemprop': 'articleBody'}).find_all('p')
        body_paras = [x for x in body_paras if len(x) != 0 and not x.has_attr('class')]

        out_paras = []
        for x in body_paras:
            if not x.find_all('figure'):
                replacement_links = []
                for child in x.findChildren('a'):
                    formatted = self.format_href(child.text, child.get('href'))
                    replacement_links.append((child.text, formatted))
                out_text = x.text
                if len(replacement_links) > 0:
                    for link in replacement_links:
                        out_text = out_text.replace(link[0], link[1])
                out_paras.append(out_text)

            tweets = self.get_tweets(self.html)

        return out_paras + tweets

    def dump_all(self):

        output = {
            'source': self.SOURCE.decode('utf-8'),
            'published': self.get_date_published().decode('utf-8'),
            'authors': self.get_authors().decode('utf-8'),
            'title': self.get_title().decode('utf-8'),
            'text': [unicode(x) for x in self.get_text()]
        }

        return output

class HuffPo_Scraper:
    '''Scrapes and parses The Huffington Post text
       Converts Links to the following format
       {click me}<hyperlink="http://www.gohere.com">
    '''
    def __init__(self, url):
        self.html = requests.get(url).text
        self.soup = BeautifulSoup(self.html)
        self.SOURCE = 'The Huffington Post'

    def get_tweets(self):

        remove_doubles = lambda x: list(set(x))

        tweet_ids = re.findall('twitter.com/.*/statuses/(\d+)', self.html) + \
                    re.findall('twitter.com/.*/status/(\d+)', self.html)
        # removes duplicates
        tweets = remove_doubles(['[tweetbegin {} tweetend]'.format(tweet_id)
                            for tweet_id in tweet_ids])
        return tweets

    def get_text(self):

        def format_link(contents, href):
            return '{}{}{}<hyperlink="{}">'.format('{', contents, '}', link.get('href'))


        body_para_class_sets = [['content-list-component-text', 'text'],
                                ['entry__body', 'js-entry-body']]

        div_sets = [self.soup.find_all('div', {'class': bp_class})
                    for bp_class in body_para_class_sets]

        out_paras = []
        for div_set in div_sets:
            for div in div_set:
                for kid in div.find_all('p'):
                    text = kid.text
                    links = [(link.contents[0], format_link(link.contents[0], link.get('href')))\
                            for link in kid.find_all('a')]

                    if len(links) > 0:
                        for link in links:
                            text =  text.replace(link[0], link[1])
                    out_paras.append(text)
        out_paras += self.get_tweets()
        return out_paras

    def get_authors(self):
        return self.soup.find('meta', {'id': 'author'})['content']

    def get_date_published(self):
        full_date = self.soup.find('meta', {'id': 'published'})['content']
        return full_date[5:7] + '/' + full_date[8:10] + '/' + full_date[:4]

    def get_title(self):
        return self.soup.find('meta', {'property': 'og:title'})['content']

    def dump_all(self):
        output = {
            'source': self.SOURCE.decode('utf-8'),
            'published': self.get_date_published().decode('utf-8'),
            'authors': self.get_authors().decode('utf-8'),
            'title': self.get_title().decode('utf-8'),
            'text': [unicode(x) for x in self.get_text()]
        }

        return output

