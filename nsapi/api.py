import datetime

import requests
from .dtypes.travel_information import TravelAdvice, StationResponse, RepresentationResponseArrivalsPayload, RepresentationResponseDeparturesPayload, \
    RepresentationResponseJourney


class APIEndpoint:
    def __init__(self, session, path):
        self.session = session
        self.path = path

    def request(self, method, path, *args, **kwargs):
        return self.session.request(method, f'{self.path}/{path}', *args, **kwargs)

    def get(self, path, *args, **kwargs):
        return self.request('GET', path, *args, **kwargs)


class NSAPI(APIEndpoint):
    # PATH = 'https://gateway.apiportal.ns.nl'

    def __init__(self, api_token):
        super().__init__(requests.Session(), 'https://gateway.apiportal.ns.nl')
        self.session.headers['Ocp-Apim-Subscription-Key'] = api_token
        self.travel_information = TravelInformationEndpoint(self)

    def request(self, method, path, *args, **kwargs):
        response = super().request(method, path, *args, **kwargs)
        response.raise_for_status()
        return response.json()


class TravelInformationEndpoint(APIEndpoint):
    def __init__(self, session):
        super().__init__(session, 'reisinformatie-api')

    def trips(self, origin, destination, **kwargs) -> TravelAdvice:
        params = {'fromStation': origin, 'toStation': destination}
        params.update(kwargs)
        return TravelAdvice(self.get('api/v3/trips', params=params))

    def stations(self, q, country=None, limit=None) -> StationResponse:
        params = {'q': q}
        if country is not None:
            params['countryCodes'] = country
        if limit is not None:
            params['limit'] = limit
        return StationResponse(self.get('api/v2/stations', params=params))

    def arrivals(self, station, limit=None) -> RepresentationResponseArrivalsPayload:
        params = {'station': station}
        if limit is not None:
            params['maxJourneys'] = limit
        return RepresentationResponseArrivalsPayload(self.get('api/v2/arrivals', params))

    def departures(self, station, limit=None) -> RepresentationResponseDeparturesPayload:
        params = {'station': station}
        if limit is not None:
            params['maxJourneys'] = limit
        return RepresentationResponseDeparturesPayload(self.get('api/v2/departures', params))

    def journey(self, train=None, journey_id=None):
        if journey_id is not None:
            params = {'id': journey_id}
        elif train is not None:
            params = {'train': train}
        else:
            raise ValueError('Specify either `train` or `journey_id`.')
        return RepresentationResponseJourney(self.get('api/v2/journey', params))
