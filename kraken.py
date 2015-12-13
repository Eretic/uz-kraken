#!/usr/bin/env python3
import pprint
import sys

from crawler import UzCrawler


def search(from_city, till_city, date):
    crawler = UzCrawler.UzCrawler()
    crawler.get()
    trains = crawler.search(from_city, till_city, date)
    pprint.pprint(trains)


if __name__ == '__main__':
    bad_command = True
    if len(sys.argv) > 1:
        if sys.argv[1] == 'search' and len(sys.argv) == 5:
            search(sys.argv[2], sys.argv[3], sys.argv[4])
            bad_command = False
    if bad_command:
        print('Available commands:')
        print('%s search <from> <till> <data>\n\t'
              'f.e. search "Киев-Пассажирский" "Харьков-Пасс"  "24.12.2015" ' % sys.argv[0])
