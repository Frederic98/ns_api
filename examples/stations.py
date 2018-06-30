import os
import nsapi as ns
import pickle

STATIONS_FILE = 'stations.pkl'

if __name__ == '__main__':
    with open('credentials.pkl', 'rb') as f:
        user, passwd = pickle.load(f)
    api = ns.NSAPI(user, passwd)

    if os.path.isfile(STATIONS_FILE):
        api.load_stations(STATIONS_FILE)
        print('Loaded station list from file')
    else:
        api.fetch_stations()
        print('Loaded station list from API')
        api.dump_stations(STATIONS_FILE)
        print('Ssved station list to file')

    print('There are {} stations in total'.format(len(api.stations)))
    
    foreign = [station for station in api.stations if station.country is not ns.StationCountry.NETHERLANDS]
    print('Found {} stations that are not in the Netherlands'.format(len(foreign)))
    countries = set([station.country for station in api.stations])
    print('Found the following countries: ' + ', '.join([country.name for country in countries]))

    stations_in_czech = [station.names.long for station in api.stations if station.country is ns.StationCountry.CZECH]
    print('The following stations are in the Czech Republic: ' + ', '.join(stations_in_czech))

    station_up = 'Utrecht'
    station_down = 'Geldermalsen'
    lat_up = float(api.get_station(station_up).location.latitude)
    lat_down = float(api.get_station(station_down).location.latitude)
    stations_in_range = [station for station in api.stations if lat_down < float(station.location.latitude) < lat_up]
    print('There are {} stations between {} and {}'.format(len(stations_in_range), station_up, station_down))
