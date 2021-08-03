from .RSSFeed import RSSFeed
import yaml

CONFIG_FILE = "config.yaml"

def rss_filter():
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


