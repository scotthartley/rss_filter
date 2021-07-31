"""Defines the RSSFeed class.
"""

from lxml import etree
import urllib.request
import yaml
from datetime import datetime

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}
CONFIG_FILE = "config.yaml"

class RSSFeed:
    """Loads an RSS feed and outputs the same feed after filtering out
    items.
    """



    def __init__(self,
                 url: str,
                 track_filters: dict,
                 filename: str,
                 other_filters: dict=None):

        self.url = url
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req) as response:
            raw_feed = response.read()
        self.root = etree.fromstring(raw_feed)

        self.track_filters = track_filters
        self.filename_root = filename
        self.other_filters = other_filters
        self.filtered = False

    def filter(self):
        namespaces = self.root.nsmap
        filename = f"{self.filename_root}.yaml"
        try:
            with open(filename, 'r') as file:
                previous_articles = yaml.load(file, Loader=yaml.FullLoader)
        except FileNotFoundError:
            previous_articles = []

        breakpoint()
        # Filter based on id and date.
        for element in self.root[0]:
            print(element.tag)
            if element.tag[:4] == "item":
                item = {}
                item['date'] = element.find(self.track_filters['date'], namespaces).text
                item['id'] = element.find(self.track_filters['id'], namespaces).text

                found = False
                for article in previous_articles:
                    if article['id'] == item['id']:
                        found = True
                        if article['date'] != item['date']:
                            self.root[0].remove(element)
                            self.log_removal(item['id'], "duplicate")

                if not found:
                    previous_articles.append(item)

        with open(filename, 'w') as file:
            yaml.dump(previous_articles, file)

        # Filter based on other filters
        if self.other_filters:
            for element in self.root[0]:
                if element.tag[:4] == "item":
                    for filt in self.other_filters:
                        for filter_id in filt:
                            element_val = element.find(filter_id, namespaces)
                            # filter_id_length = len(filter_id)
                            # breakpoint()
                            # print(element.tag[:filter_id_length])
                            # if element.tag[:filter_id_length] == filter_id:
                            #     item = element.find(filter_id, namespaces).text
                            #     if element.text == filt[filter_id]:
                            #         self.root[0].remove(element)
                            #         self.log_removal(element.find(self.track_filters['id']), "filter")
        self.filtered = True


    def output_feed(self):
        if not self.filtered:
            self.filter()

        filename = f"{self.filename_root}.xml"
        tree = etree.ElementTree(self.root)
        with open(filename, 'wb') as file:
            tree.write(file)

    def log_removal(self, id, reason):
        filename = f"{self.filename_root}.log"

        with open(filename, 'a') as file:
            file.write(f"{datetime.now()}: Removed {id} ({reason})\n")

if __name__ == "__main__":
    with open(CONFIG_FILE) as file:
        configuration = yaml.load(file.read(), Loader=yaml.FullLoader)

    journals = []
    for journal_entry in configuration:
        url = configuration[journal_entry]['url']
        track_filters = configuration[journal_entry]['track']
        filename = configuration[journal_entry]['file']
        if 'filter' in configuration[journal_entry]:
            other_filters = configuration[journal_entry]['filter']
        else:
            other_filters = None
        feed = RSSFeed(url, track_filters, filename, other_filters)
        journals.append(feed)

    for journal in journals:
        journal.output_feed()



