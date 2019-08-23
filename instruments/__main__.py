import argparse

from instruments.extract import webscrape
from instruments.transform import document


parser = argparse.ArgumentParser()

parser.add_argument('--scrape', action='store_true', help='scrape data from Gibson website')
parser.add_argument('--mongo', action='store_true', help='insert data into MongoDB')

args = parser.parse_args()

if args.scrape:
    webscrape.main()

if args.mongo:
    document.main()
