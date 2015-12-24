from kraken.webkraken import db


class Station(db.Model):
    __tablename__ = 'stations'

    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.String(), index=True, unique=True)
    name_ru = db.Column(db.String(), index=True)
    name_en = db.Column(db.String(), index=True)
    name_ua = db.Column(db.String(), index=True)

    def __init__(self, station_id, name_ru='', name_en='', name_ua=''):
        self.station_id = station_id
        self.name_ru = name_ru
        self.name_en = name_en
        self.name_ua = name_ua

    def __repr__(self):
        return '<Station id={} station_id={}>'.format(self.id, self.station_id)


class UzStations:
    def __init__(self, conn):
        self.conn = conn

    def put(self, station):
        self.conn.session.add(station)
        self.conn.session.commit()

    def get_by_name(self, name):
        sts = Station.query.all()
        for s in sts:
            if s.name_ru == name or s.name_en == name or s.name_ua == name:
                return s
        return None


class Request(db.Model):
    __tablename__ = 'requests'

    id = db.Column(db.Integer, primary_key=True)
    time = db.Column(db.DateTime)
    type = db.Column(db.String())
    request = db.Column(db.String())
