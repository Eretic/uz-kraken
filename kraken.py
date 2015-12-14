#!/usr/bin/env python3
import sys

from crawler import UzCrawler


def print_train(train):
    assert isinstance(train, UzCrawler.Train)
    print('Поезд %s %s %s' % (train.num, train.source.station, train.destination.station))
    print('\tОтправление: %s\n\tПрибытие: %s' % (train.source.src_date, train.destination.src_date))
    print('\t', ', '.join(['%s: %d' % (c['title'], c['places']) for c in train.coaches]), sep='')


def search(from_city, till_city, date):
    assert isinstance(from_city, str)
    if 'a' <= from_city.lower()[0] <= 'z':
        lang = 'en'
    else:
        lang = 'ru'
    crawler = UzCrawler.UzCrawler(lang)
    crawler.get()
    trains = crawler.search(from_city, till_city, date)
    for t in trains:
        print_train(t)


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
