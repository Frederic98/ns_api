from typing import Union
import logging

from nsapi import NSAPI
from nsapi.dtypes.travel_information import TripOriginDestination, Arrival

logging.basicConfig(level=logging.INFO)


with open('token.txt') as f:
    api_token = f.read().strip()
api = NSAPI(api_token)


# Plan a trip
def format_trip_station(station: TripOriginDestination):
    time = station.actualDateTime if station.actualDateTime is not None else station.plannedDateTime
    track = station.actualTrack if station.actualTrack is not None else station.plannedTrack
    return f'({time:%H:%M}) {station.name} [{track}]'

station_name = 'geldermalsen'
station = api.travel_information.stations(station_name).payload[0]
print(f'{station.namen.lang} station:')
names = {station.namen.kort, station.namen.middel, station.namen.lang, station.namen.festive}
names.discard(None)
print(f' - Names: {", ".join(names)}')
print(f' - Abbreviation: {station.code}')
print(f' - UIC: {station.UICCode}')
print(f' - Tracks: {" - ".join(track.spoorNummer for track in station.sporen)}')
print()

advice = api.travel_information.trips('ehv', station.code)
trip = [trip for trip in advice.trips if trip.optimal][0]
print(f'{trip.legs[0].origin.name} - {trip.legs[-1].destination.name} ({trip.plannedDurationInMinutes} minutes)')
if len(trip.legs) > 1:
    for leg in trip.legs:
        print(f' - {format_trip_station(leg.origin)} - {format_trip_station(leg.destination)}')
print()

journey = api.travel_information.journey(journey_id=trip.legs[0].journeyDetailRef).payload
print(journey.stops[0].plannedStock.trainType)
print(f'{journey.stops[0].stop.namen.lang} - {journey.stops[-1].stop.namen.lang}')
for stop in journey.stops:
    print(f'|{"->" if stop.status != "PASSING" else "  "} {stop.stop.namen.lang}')
print()

# Get arrivals on station
arrivals = api.travel_information.arrivals(station.code, limit=15)
print(f'Arrivals for {station.namen.lang}:')
origin_length = max(len(train.origin) for train in arrivals.payload.arrivals)
for train in arrivals.payload.arrivals:
    time = train.actualDateTime if train.actualDateTime is not None else train.plannedDateTime
    track = train.actualTrack if train.actualTrack is not None else train.plannedTrack
    print(f'({time:%H:%M}) {train.origin:<{origin_length}} [{track}] {train.name}')
print()

# Get arrivals on station
departures = api.travel_information.departures(station.code, limit=15)
print(f'Departures for {station.namen.lang}:')
direction_length = max(len(train.direction) for train in departures.payload.departures)
for train in departures.payload.departures:
    time = train.actualDateTime if train.actualDateTime is not None else train.plannedDateTime
    track = train.actualTrack if train.actualTrack is not None else train.plannedTrack
    print(f'({time:%H:%M}) {train.direction:<{direction_length}} [{track}]  {train.name} {train.departureStatus}')
print()
