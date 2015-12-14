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
    def __init__(self, lang='ru'):
        self.user_agent = 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.80 Safari/537.36'
        self.lang = lang
        self.cookies = None
        self.token = ''
        self.server = ''
        self.session_id = ''
        self.last_coaches = list()

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

    def station(self, name):
        url = '%s/purchase/station/' % self.lang
        add_headers = dict()
        add_headers['Referer'] = 'http://booking.uz.gov.ua/%s/' % self.lang
        add_headers['Host'] = 'booking.uz.gov.ua'
        add_headers['Proxy-Connection'] = 'keep-alive'
        add_headers['Origin'] = 'http://booking.uz.gov.ua'
        add_headers['User-Agent'] = self.user_agent
        resp = requests.post(UZ_BASE + url + name + '/',
                             cookies=self.cookies,
                             headers=add_headers)
        if not resp.ok:
            print(resp.status_code)
            return None
        stations = json.loads(resp.content.decode('utf-8'))
        ids = {x['title']: x['station_id'] for x in stations['value']}
        codes = UzTownCode()
        codes.put_all(ids)
        pprint.pprint(stations)
        # self.cookies = resp.cookies
        return stations

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
        add_headers['GV-Referer'] = 'http://booking.uz.gov.ua/%s/' % self.lang
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
        url = '%s/purchase/search/' % self.lang
        for times in range(2):
            coder = UzTownCode()
            from_city_id = coder.get(from_city)
            to_city_id = coder.get(to_city)

            if not from_city_id:
                print('I do not know id for ' + from_city)
                self.station(from_city)
            elif not to_city_id:
                print('I do not know id for ' + to_city)
                self.station(to_city)
            else:
                break
        else:
            print('I can not get id for one of the cities')
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
        if not resp.ok:
            print('Can not get trains information:', resp.status_code)
            self.dump_cookies()
            return None
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

    def coaches(self, train, coach_type, station_from, station_to):
        assert isinstance(train, Train)
        url = '%s/purchase/coaches/' % self.lang

        coder = UzTownCode()
        data = dict()
        data['station_id_from'] = coder.get(station_from)
        data['station_id_till'] = coder.get(station_to)
        data['train'] = train.num
        data['coach_type'] = coach_type
        data['model'] = train.model
        data['date_dep'] = train.source.date
        data['another_ec'] = 0
        data['round_trip'] = 0

        resp = self.uz_post(url, data)
        if not resp.ok:
            print(resp.status_code)
            return None
        coaches = json.loads(resp.content.decode('utf-8'))
        coaches = coaches['value']
        self.last_coaches = coaches['coaches']
        return resp

    def coach(self, train, coach_num, station_from, station_to):
        assert isinstance(train, Train)
        url = '%s/purchase/coach/' % self.lang
        data = dict()
        coder = UzTownCode()

        data['station_id_from'] = coder.get(station_from)
        data['station_id_till'] = coder.get(station_to)
        data['train'] = train.num

        for c in self.last_coaches:
            if c['num'] == coach_num:
                coach_class = c['coach_class']
                coach_type_id = c['coach_type_id']
                break
        else:
            print('Can not find this coach in the train.')
            return None

        data['coach_num'] = coach_num
        data['coach_class'] = coach_class
        data['coach_type_id'] = coach_type_id

        data['date_dep'] = train.source.date
        data['change_scheme'] = 1

        resp = self.uz_post(url, data)
        if not resp.ok:
            print(resp.status_code)
            return None
        coaches = json.loads(resp.content.decode('utf-8'))
        pprint.pprint(coaches)
        return resp


def get_start_page():
    crawler = UzCrawler()
    crawler.get()
    print('Search stations')

    station_from = 'Киев'
    station_to = 'Харьков'

    crawler.station(station_from)
    crawler.station(station_to)
    print('Search trains')
    trains = crawler.search(station_from, station_to, '24.12.2015')
    train = trains[0]
    for x in range(1):
        crawler.coaches(train, train.coaches[0]['letter'], station_from, station_to)
        time.sleep(1)
    crawler.coach(train, 3, station_from, station_to)


if __name__ == '__main__':
    print('Test UzCrawler')
    get_start_page()
