import os.path
import time
import json
import pickle
import pprint
import requests

from crawler import JJDecoder

UZ_BASE = 'http://booking.uz.gov.ua/'


class UzTownCode:
    def __init__(self, path=None):
        self.database = dict()
        if not path:
            path = 'uz_station_codes.txt'
        self.path = path
        if os.path.exists(self.path):
            with open(path, 'rb') as f:
                self.database = pickle.load(f)
        else:
            self.database = dict()

    def get(self, station):
        return self.database.get(station, '')

    def put(self, station, station_id):
        if station not in self.database:
            self.database[station] = station_id
            self.save()

    def put_all(self, data):
        self.database.update(data)
        self.save()

    def save(self):
        print('Save database')
        with open(self.path, 'wb') as f:
            pickle.dump(self.database, f)


class Point:
    def __init__(self, data=None):
        if not data:
            data = dict()
        self.date = data.get('date', 0)
        self.src_date = data.get('src_date', '')
        self.station = data.get('station', '')
        self.station_id = data.get('station_id', '')
        code = UzTownCode()
        code.put(self.station, self.station_id)

    def __repr__(self):
        return '<Point where=%s when=%s>' % (self.station, self.date)


class Train:
    def __init__(self, data=None):
        if not data:
            data = dict()
        self.category = data.get('category', -1)
        self.model = data.get('model', -1)
        self.num = data.get('num', '')
        self.source = Point(data.get('from', dict()))
        self.destination = Point(data.get('till', dict()))
        self.coaches = data.get('types', list())

    def __repr__(self):
        return '<Train num=%s\n\tfrom=%s\n\ttill=%s>' % (self.num, self.source, self.destination)


class UzCrawler:
    def __init__(self):
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
        self.cookies = None
        self.token = ''
        self.server = ''
        self.session_id = ''

    def get(self):
        page = UZ_BASE
        headers = dict()
        headers['User-Agent'] = self.user_agent
        resp = requests.get(page, headers=headers, cookies=self.cookies)
        self.cookies = resp.cookies
        raw_token = resp.content.decode('utf-8')
        marker_start = "_gaq.push(['_trackPageview']);"
        marker_stop = "(function ()"
        t_start = raw_token.find(marker_start)
        t_stop = raw_token.find(marker_stop, t_start)
        if t_start != -1 and t_stop != -1:
            raw_token = raw_token[t_start + len(marker_start):t_stop]
            decoded_token = JJDecoder.decode(raw_token)
            self.token = decoded_token[decoded_token.find('", "') + 4:-3]
        for c in self.cookies:
            if c.name == 'HTTPSERVERID':
                self.server = c.value
            elif c.name == '_gv_sessid':
                self.session_id = c.value
        return resp

    def dump_cookies(self):
        if not self.cookies:
            print('Cookies is not found')
            return
        for c in self.cookies:
            pprint.pprint(c)

    def uz_post(self, url, post_data):
        add_headers = dict()
        add_headers['Accept'] = 'text/html,application/xhtml+xml,application/xml;q=0.9,*;q=0.8'
        add_headers['Accept-Language'] = 'ru-RU,ru;q=0.8,en-US;q=0.6,en;q=0.4,bg;q=0.2'
        add_headers['GV-Token'] = self.token
        add_headers['GV-Unique-Host'] = 1
        add_headers['GV-Ajax'] = 1
        add_headers['GV-Screen'] = '1920x1080'
        add_headers['GV-Referer'] = 'http://booking.uz.gov.ua/ru/'
        add_headers['Referer'] = 'http://booking.uz.gov.ua/ru/'
        add_headers['Host'] = 'booking.uz.gov.ua'
        add_headers['Proxy-Connection'] = 'keep-alive'
        add_headers['Origin'] = 'http://booking.uz.gov.ua'
        add_headers['User-Agent'] = self.user_agent
        resp = requests.post(UZ_BASE + url, data=post_data,
                             cookies=self.cookies,
                             headers=add_headers)
        return resp

    def search(self, from_city, to_city, when):
        url = 'ru/purchase/search/'
        coder = UzTownCode()
        from_city_id = coder.get(from_city)
        to_city_id = coder.get(to_city)

        if not from_city_id:
            print('I do not know id for ' + from_city)
            return None
        if not to_city_id:
            print('I do not know id for ' + to_city)
            return None

        data = dict()
        data['station_id_from'] = from_city_id
        data['station_id_till'] = to_city_id
        data['station_from'] = from_city
        data['station_till'] = to_city
        data['date_dep'] = when
        data['time_dep'] = '00:00'
        data['time_dep_till'] = ''
        data['another_ec'] = 0
        data['search'] = ''

        resp = self.uz_post(url, data)
        trains = json.loads(resp.content.decode('utf-8'))
        if not trains['error']:
            trains = trains['value']
        else:
            print('Error in search')
            pprint.pprint(trains)
            return None
        # self.cookies = resp.cookies
        trains = [Train(x) for x in trains]

        return trains

    def coaches(self, train='724K', coach_type='C2'):
        url = 'ru/purchase/coaches/'
        data = dict()
        data['station_id_from'] = 2200001
        data['station_id_till'] = 2204001
        data['train'] = train
        data['coach_type'] = coach_type
        data['model'] = 1
        data['date_dep'] = 1451129700
        data['another_ec'] = 0
        data['round_trip'] = 0

        resp = self.uz_post(url, data)
        if not resp.ok:
            print(resp.status_code)
            return None
        coaches = json.loads(resp.content.decode('utf-8'))
        pprint.pprint(coaches)
        return resp

    def coach(self, train='724K', coach_type='C2'):
        url = 'ru/purchase/coaches/'
        data = dict()
        data['station_id_from'] = 2200001
        data['station_id_till'] = 2204001
        data['train'] = train
        data['coach_type'] = coach_type
        data['model'] = 1
        data['date_dep'] = 1451129700
        data['another_ec'] = 0
        data['round_trip'] = 0

        resp = self.uz_post(url, data)
        if not resp.ok:
            print(resp.status_code)
            return None
        coaches = json.loads(resp.content.decode('utf-8'))
        pprint.pprint(coaches)
        return resp


def get_start_page():
    crawler = UzCrawler()
    resp = crawler.get()
    for h in resp.headers:
        pprint.pprint(h)
    pprint.pprint(resp.cookies)
    pprint.pprint(resp.content)
    crawler.dump_cookies()
    print('Search trains')
    trains = crawler.search('Киев-Пассажирский', 'Харьков-Пасс', '24.12.2015')
    pprint.pprint(trains)
    crawler.dump_cookies()
    time.sleep(5)
    for x in range(5):
        crawler.coaches()
        time.sleep(1)

if __name__ == '__main__':
    print('Test UzCrawler')
    get_start_page()
