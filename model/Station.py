from webkraken import db


class Station(db.Model):
    __tablename__ = 'stations'

    id = db.Column(db.Integer, primary_key=True)
    station_id = db.Column(db.String())
    name_ru = db.Column(db.String())
    name_en = db.Column(db.String())
    name_ua = db.Column(db.String())

    def __init__(self, station_id, name_ru='', name_en='', name_ua=''):
        self.station_id = station_id
        self.name_ru = name_ru
        self.name_en = name_en
        self.name_ua = name_ua

    def __repr__(self):
        return '<id {}>'.format(self.id)
