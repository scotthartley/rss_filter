"""Defines the RSSFeed class.
"""

from lxml import etree
import urllib.request
import yaml
from datetime import datetime

HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36'}

ITEM_TAG = "item"

class RSSFeed:
    """Loads an RSS feed and outputs the same feed after filtering out
    items.
    """


    def __init__(self,
                 url: str,
                 track_filters: dict,
                 filename_root: str,
                 other_filters: dict=None):

        self.url = url
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req) as response:
            raw_feed = response.read()
        self.root = etree.fromstring(raw_feed)

        self.track_filters = track_filters
        self.filename_root = filename_root
        self.other_filters = other_filters
        self.filtered = False


    @staticmethod
    def locate_all_elements(node, target, namespaces, result):
        """Recursively search through the node to identify all instances
        of the target tag.

        """
        for element in node:
            # Need to remove namespace and prefix from tag name.
            if etree.QName(element).localname == target:
                result.append(element)
            RSSFeed.locate_all_elements(element, target, namespaces, result)
        return result


    @staticmethod
    def remove(element):
        """Remove an element from root.

        """
        parent = element.getparent()
        parent.remove(element)


    def filter(self):
        """Filter out duplicated items and those that meet the filter
        criteria.

        """
        namespaces = self.root.nsmap
        filename = f"{self.filename_root}.yaml"
        try:
            with open(filename, 'r') as file:
                previous_articles = yaml.load(file, Loader=yaml.FullLoader)
        except FileNotFoundError:
            previous_articles = []

        current_articles = RSSFeed.locate_all_elements(self.root, ITEM_TAG,
                                                         namespaces, [])

        for article in current_articles:
            article_id = article.find(
                    self.track_filters['id'], namespaces).text
            article_date = article.find(
                    self.track_filters['date'], namespaces).text

            found = False
            removed = False

            # Filter based on id and date
            for previous_article in previous_articles:
                if article_id == previous_article['id']:
                    found = True
                    if article_date != previous_article['date']:
                        removed = True
                        self.remove(article)
                        self.log_removal(article_id, "duplicate")
            if not found:
                previous_articles.append({'id': article_id,
                        'date': article_date})

            # Filter based on other criteria
            if (not removed) and self.other_filters:
                for filt in self.other_filters:
                    for tag in filt:
                        element = article.find(tag, namespaces)
                        if element.text == filt[tag]:
                            self.remove(article)
                            self.log_removal(article_id, "filtered")

        with open(filename, 'w') as file:
            yaml.dump(previous_articles, file)

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
