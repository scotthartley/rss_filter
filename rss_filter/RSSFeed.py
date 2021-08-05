"""Defines the RSSFeed class.
"""

from lxml import etree
import urllib.request
import yaml
from datetime import datetime

# Headers for the urllib request
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
        self.filename_log = f"{self.filename_root}.log"
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
        """Remove an element from the tree.
        """
        parent = element.getparent()
        parent.remove(element)


    def log_removal(self, id, reason):
        """Log an article removal
        """
        with open(self.filename_log, 'a') as file:
            file.write(f"{datetime.now()}: Removed {id} ({reason})\n")


    def log_other(self, reason):
        """Log other issues
        """
        with open(self.filename_log, 'a') as file:
            file.write(f"{datetime.now()}: {reason}\n")


    def filter(self):
        """Filter out duplicated items and those that meet the filter
        criteria.
        """
        namespaces = self.root.nsmap

        # Load the log of previous articles
        filename = f"{self.filename_root}.yaml"
        try:
            with open(filename, 'r') as file:
                previous_articles = yaml.load(file, Loader=yaml.FullLoader)
        except FileNotFoundError:
            previous_articles = []

        # Find all articles within the feed
        current_articles = RSSFeed.locate_all_elements(self.root, ITEM_TAG,
                                                       namespaces, [])

        for article in current_articles:
            # Filter based on id and date
            article_id_element = article.find(
                    self.track_filters['id'], namespaces)
            article_date_element = article.find(
                    self.track_filters['date'], namespaces)

            if ((article_id_element is not None)
                    and (article_date_element is not None)):
                article_id = article_id_element.text
                article_date = article_date_element.text[:self.track_filters['date_chars']]
                found = False
                removed = False
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
                            elements = article.findall(tag, namespaces)
                            if len(elements) == 0:
                                self.log_other(f'"{tag}" tag not found')
                            else:
                                for element in elements:
                                    if element.text == filt[tag]:
                                        self.remove(article)
                                        self.log_removal(article_id, "filtered")
            else:
                self.log_other(f"Article id or date not found")

        with open(filename, 'w') as file:
            yaml.dump(previous_articles, file)

        self.filtered = True


    def output_feed(self):
        """Save the updated feed.
        """
        if not self.filtered:
            self.filter()

        filename = f"{self.filename_root}.xml"
        tree = etree.ElementTree(self.root)
        with open(filename, 'wb') as file:
            tree.write(file)
