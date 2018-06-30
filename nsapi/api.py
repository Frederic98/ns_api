from collections import namedtuple
from datetime import datetime, timedelta
from typing import Union, List
from xml.etree import ElementTree
import pickle
import requests
from requests.compat import urljoin

from . import strftime, strptime, Delay, Duration                    # Time things
from . import StationType, StationCountry, Train, Carrier, Status   # Enums


#########################
# Departure information #
#########################
class Track(str):
    def __new__(cls, track, changed=False):
        if track is None:
            track = ''
        self = str.__new__(cls, track)
        self.changed = changed
        return self

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


class Departure:
    ride_number = 0
    departure_time = datetime.utcfromtimestamp(0)
    destination = ''
    train_type = Train.UNKNOWN
    carrier = Carrier.UNKNOWN
    departure_track = Track(0)
    departure_delay = Delay(0)
    route = ''
    journy_hint = ''
    remarks = ''

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_xml(cls, tree: ElementTree.Element):
        """
        Create and return a Departure instance from an XML tree in the following structure:

        <VertrekkendeTrein>
            <RitNummer>6079</RitNummer>
            <VertrekTijd>2018-05-25T22:13:00+0200</VertrekTijd>
            <VertrekVertraging>PT19M</VertrekVertraging>
            <VertrekVertragingTekst>+19 min</VertrekVertragingTekst>
            <EindBestemming>Tiel</EindBestemming>
            <TreinSoort>Sprinter</TreinSoort>
            <Vervoerder>NS</Vervoerder>
            <VertrekSpoor wijziging="false">4b</VertrekSpoor>
        </VertrekkendeTrein>
        """
        self = cls()
        self.ride_number = int(tree.findtext('RitNummer'))
        self.departure_time = strptime(tree.findtext('VertrekTijd'))
        self.destination = tree.findtext('EindBestemming')
        self.train_type = Train(tree.findtext('TreinSoort'))
        self.carrier = Carrier(tree.findtext('Vervoerder'))

        track = tree.find('VertrekSpoor')   # type: ElementTree.Element
        self.departure_track = Track(track.text, track.attrib['wijziging'] == 'true')
        self.departure_delay = Delay(tree.findtext('VertrekVertraging', 0), tree.findtext('VertrekVertragingTekst'))

        route = tree.find('RouteTekst')     # type: ElementTree.Element
        if route is not None:
            self.route = route.text
        journy_hint = tree.find('ReisTip')
        if journy_hint is not None:
            self.journy_hint = journy_hint.text
        remarks = tree.find('Opmerkingen')  # type: ElementTree.Element
        if remarks is not None:
            self.remarks = '\n'.join([rem.text.strip() for rem in remarks.findall('Opmerking')])
        return self

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


#######################
# Station information #
#######################
StationNames = namedtuple('StationNames', 'short medium long')
StationLocation = namedtuple('StationLocation', 'latitude longitude')


class Station:
    code = ''
    type = StationType.UNKNOWN
    names = StationNames('', '', '')
    country = StationCountry.UNKNOWN
    UICCode = 0
    location = StationLocation(0, 0)
    synonyms = []

    def __init__(self, **kwargs):
        for key, value in kwargs.items():
            setattr(self, key, value)

    @classmethod
    def from_xml(cls, tree: ElementTree.Element):
        """
        Create and return a Station instance from an XML tree in the following structure:

        <Station>
            <Code>GDM</Code>
            <Type>knooppuntStoptreinstation</Type>
            <Namen>
                <Kort>Geldermlsn</Kort>
                <Middel>Geldermalsen</Middel>
                <Lang>Geldermalsen</Lang>
            </Namen>
            <Land>NL</Land>
            <UICCode>8400244</UICCode>
            <Lat>51.88301</Lat>
            <Lon>5.27127</Lon>
            <Synoniemen></Synoniemen>
        </Station>
        """
        self = cls()
        self.code = tree.findtext('Code')
        self.type = StationType(tree.findtext('Type'))
        self.names = StationNames(*[tree.find('Namen').findtext(t) for t in ('Kort', 'Middel', 'Lang')])
        self.location = StationLocation(tree.findtext('Lat'), tree.findtext('Lon'))
        self.country = StationCountry(tree.findtext('Land'))
        self.UICCode = int(tree.findtext('UICCode'))
        self.synonyms = [s.text for s in tree.find('Synoniemen').findall('Synoniem')]
        return self

    @property
    def identifiers(self):
        return {self.code, *self.names, *self.synonyms}

    def __str__(self):
        return self.names.long

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


################
# Notification #
################
class Notification:
    id = ''
    serious = False
    text = ''

    def __init__(self, id, serious, text):
        self.id = id
        self.serious = serious
        self.text = text

    @classmethod
    def from_xml(cls, tree: ElementTree.Element):
        id = tree.findtext('Id')
        serious = tree.findtext('Ernstig') == 'true'
        text = tree.findtext('Text')
        return cls(id, serious, text)

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


###########
# Journey #
###########
class Journey:
    notifications = []
    transfers = 0
    duration_planned = timedelta()
    duration_actual = timedelta()
    optimal = False
    departure_time_planned = datetime.utcfromtimestamp(0)
    departure_time_actual = datetime.utcfromtimestamp(0)
    arrival_time_planned = datetime.utcfromtimestamp(0)
    arrival_time_actual = datetime.utcfromtimestamp(0)
    status = Status.UNKNOWN
    parts = []      # type: List(JourneyPart)

    def __init__(self, **kwargs):
        for key, value in kwargs:
            setattr(self, key, value)

    @classmethod
    def from_xml(cls, tree: ElementTree.Element):
        self = cls()
        self.notifications = [Notification.from_xml(notif) for notif in tree.findall('Melding')]
        self.transfers = int(tree.findtext('AantalOverstappen'))
        self.duration_planned = Duration(tree.findtext('GeplandeReisTijd'))
        self.duration_actual = Duration(tree.findtext('ActueleReisTijd'))
        self.optimal = tree.findtext('Optimaal') == 'true'
        self.departure_time_planned = strptime(tree.findtext('GeplandeVertrekTijd'))
        self.departure_time_actual = strptime(tree.findtext('ActueleVertrekTijd'))
        self.arrival_time_planned = strptime(tree.findtext('GeplandeAankomstTijd'))
        self.arrival_time_actual = strptime(tree.findtext('ActueleAankomstTijd'))
        self.status = Status(tree.findtext('Status'))
        self.parts = [JourneyPart.from_xml(part) for part in tree.findall('ReisDeel')]
        return self

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


class JourneyPart:
    carrier = Carrier.UNKNOWN
    train_type = Train.UNKNOWN
    ride_number = 0
    status = Status.UNKNOWN
    stops = []      # type: List(JourneyStop)

    def __init__(self, **kwargs):
        for key, value in kwargs:
            setattr(self, key, value)

    @classmethod
    def from_xml(cls, tree: ElementTree.Element):
        self = cls()
        self.carrier = Carrier(tree.findtext('Vervoerder'))
        self.train_type = Train(tree.findtext('VervoerType'))
        self.ride_number = int(tree.findtext('RitNummer'))
        self.status = Status(tree.findtext('Status'))
        self.stops = []
        for stop in tree.findall('ReisStop'):
            self.stops.append(JourneyStop(stop.findtext('Naam'), stop.findtext('Tijd'), stop.findtext('Spoor')))
        return self

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


class JourneyStop:
    station = ''        # type: Union(str, Station)
    time = datetime.utcfromtimestamp(0)
    track = Track(None)

    def __init__(self, station, time, track=None):
        self.station = station
        if isinstance(time, str):
            time = strptime(time)
        self.time = time
        if not isinstance(track, Track):
            track = Track(track)
        self.track = track

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.__dict__ == other.__dict__

    def __ne__(self, other):
        return not self.__eq__(other)


####################
# NS API interface #
####################
class NSAPI:
    BASEURL = 'http://webservices.ns.nl/{}'

    def __init__(self, usr, passwd):
        self.usr = usr
        self.passwd = passwd
        self.stations = []

    def request(self, url):
        url = urljoin(self.BASEURL, url)
        resp = requests.get(url, auth=(self.usr, self.passwd))
        if resp.status_code == 400:
            raise RuntimeError('Couldn\'t authenticate at server')
        resp.encoding = 'utf-8'
        data = ElementTree.fromstring(resp.text)
        if data.tag == 'error':
            raise RuntimeError(data.findtext('message'))
        return data

    def get_departures(self, station):
        resp = self.request('ns-api-avt?station={}'.format(station))
        departures = []
        for departure in resp:
            departures.append(Departure.from_xml(departure))
        return departures

    def get_journey(self, from_station, to_station, via_station=None,
                    past_advices=None, next_advices=None, time=None, time_departure=True,
                    hsl_allow=True, yearcard=False):
        url = 'ns-api-treinplanner?'
        keymap = {'fromStation': from_station,
                  'toStation': to_station,
                  'viaStation': via_station,
                  'previousAdvices': past_advices,
                  'nextAdvices': next_advices,
                  'dateTime': time,
                  'Departure': time_departure,
                  'hslAllowed': hsl_allow,
                  'yearCArd': yearcard}
        url += '&'.join(['{}={}'.format(key,val) for key,val in keymap.items() if val is not None])
        resp = self.request(url)
        options = [Journey.from_xml(option) for option in resp]
        return options

    def get_station(self, station) -> Station:
        station = station.lower()
        for s in self.stations:
            if station in [i.lower() for i in s.identifiers]:
                return s

    def load_stations(self, file):
        self.stations.clear()
        if hasattr(file, 'read'):
            stations = pickle.load(file)
        elif isinstance(file, bytes):
            stations = pickle.loads(file)
        else:
            with open(file, 'rb') as f:
                stations = pickle.load(f)
        self.stations.extend(stations)

    def dump_stations(self, file):
        with open(file, 'wb') as f:
            pickle.dump(self.stations, f)

    def fetch_stations(self):
        resp = self.request('ns-api-stations-v2')
        self.stations.clear()
        self.stations.extend([Station.from_xml(station) for station in resp])
