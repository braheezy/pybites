#!/usr/bin/python3
import xml.etree.ElementTree as ET
from collections import Counter
from pprint import pprint
import difflib

TOP_NUMBER = 10
RSS_FEED = 'rss.xml'
SIMILAR = 0.87


def get_tags():
    """Find all tags in RSS_FEED.
    Replace dash with whitespace."""
    tree = ET.parse(RSS_FEED)

    tags = Counter()
    # Iterate over all 'item' Elements and get text of 'category' children.
    for item in tree.getroot().iter('item'):
        for category in item.findall('category'):
            tags[category.text.lower().replace('-', ' ')] += 1
    # pprint(tags)
    return tags


def get_top_tags(tags):
    """Get the TOP_NUMBER of most common tags"""
    return tags.most_common(TOP_NUMBER)


def get_similarities(tags):
    """Find set of tags pairs with similarity ratio of > SIMILAR"""
    # Get list of tags
    words = sorted(list(tags.keys()))

    similarities = dict()
    # Compare each word to every word after it
    for i, word in enumerate(words):
        possibilities = words[i + 1:]
        matches = difflib.get_close_matches(word,
                                            possibilities,
                                            cutoff=SIMILAR)
        # print('word: {}, matches: {}'.format(word, matches))
        if matches:
            similarities[word] = matches[0]

    # pprint(similarities)
    return similarities


if __name__ == "__main__":
    tags = get_tags()
    top_tags = get_top_tags(tags)
    print('* Top {} tags:'.format(TOP_NUMBER))
    for tag, count in top_tags:
        print('{:<20} {}'.format(tag, count))
    similar_tags = dict(get_similarities(tags))
    print()
    print('* Similar tags:')
    for singular, plural in similar_tags.items():
        print('{:<20} {}'.format(singular, plural))
