# coding=utf-8
from flask import Flask, request
from crawler import UzCrawler


app = Flask(__name__)


def print_train(train):
    assert isinstance(train, UzCrawler.Train)
    out_str = '<pre>'
    out_str += 'Поезд %s %s %s\n' % (train.num, train.source.station, train.destination.station)
    out_str += '\tОтправление: %s\n\tПрибытие: %s\n' % (train.source.src_date, train.destination.src_date)
    out_str += '\t' + ', '.join(['%s: %d' % (c['title'], c['places']) for c in train.coaches])
    out_str += '</pre>'
    return out_str

@app.route('/')
def hello():
    return 'Hello from Kraken'

@app.route('/search', methods=['GET'])
def search():
    from_city = request.args.get('from_city', '')
    till_city = request.args.get('till_city', '')
    date = request.args.get('date', '')
    if 'a' <= from_city.lower()[0] <= 'z':
        lang = 'en'
    else:
        lang = 'ru'
    crawler = UzCrawler.UzCrawler(lang)
    crawler.get()
    stations = crawler.station(from_city)
    if not stations:
        return 'Не могу определить что за станция: %s' % from_city
    else:
        from_station = stations[0]['title']
    stations = crawler.station(till_city)
    if not stations:
        return 'Не могу определить что за станция: %s' % till_city
    else:
        to_station = stations[0]['title']

    trains = crawler.search(from_station, to_station, date)
    if trains:
        return '\n'.join([print_train(t) for t in trains])
    else:
        return 'Поезда в заданном направлении не найдены'


if __name__ == '__main__':
    app.run(debug=True)
