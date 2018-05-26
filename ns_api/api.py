from collections import namedtuple
from enum import Enum
from datetime import datetime
from xml.etree import ElementTree
import pickle
import requests
from requests.compat import urljoin

from . import strftime, strptime, Delay                     # Time things
from . import StationType, StationCountry, Train, Carrier   # Enums


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
    location = StationLocation(0,0)
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
