import typing
import datetime

from . import NSData


class Arrival(NSData):
    origin: typing.Optional[str]
    name: str
    plannedDateTime: typing.Optional[datetime.datetime]
    plannedTimeZoneOffset: typing.Optional[int]
    actualDateTime: typing.Optional[datetime.datetime]
    actualTimeZoneOffset: typing.Optional[int]
    plannedTrack: typing.Optional[str]
    actualTrack: typing.Optional[str]
    product: "Product"
    trainCategory: str
    cancelled: bool
    journeyDetailRef: typing.Optional[str]
    messages: list["Message"]
    arrivalStatus: str


class ArrivalOrDeparture(NSData):
    product: "Product"
    origin: typing.Optional["Station"]
    destination: typing.Optional["Station"]
    plannedTime: typing.Optional[datetime.datetime]
    actualTime: typing.Optional[datetime.datetime]
    delayInSeconds: typing.Optional[int]
    plannedTrack: typing.Optional[str]
    actualTrack: typing.Optional[str]
    cancelled: bool
    punctuality: typing.Optional[float]
    crowdForecast: str
    shorterStockClassification: typing.Optional[str]
    stockIdentifiers: typing.Optional[list[str]]


class ArrivalsPayload(NSData):
    source: str
    arrivals: list["Arrival"]


class CalamitiesResourceCalamity(NSData):
    id: typing.Optional[str]
    titel: typing.Optional[str]
    beschrijving: typing.Optional[str]
    lastModified: typing.Optional[int]
    type: typing.Optional[str]
    url: typing.Optional[str]
    buttonPositie: typing.Optional[str]
    laatstGewijzigd: typing.Optional[int]
    volgendeUpdate: typing.Optional[int]
    calltoactionbuttons: typing.Optional[list["CallToActionButton"]]
    bodyitems: typing.Optional[list["CalamityBodyItem"]]


class CalamitiesResponse(NSData):
    calamiteit: typing.Optional["CalamitiesResourceCalamity"]
    meldingen: typing.Optional[list["CalamitiesResourceCalamity"]]


class CalamityBodyItem(NSData):
    objectType: str
    content: typing.Optional[str]
    titel: typing.Optional[str]
    downloads: typing.Optional[list["Download"]]
    links: typing.Optional[list["Link"]]


class CallToActionButton(NSData):
    callToAction: typing.Optional[str]
    url: typing.Optional[str]
    type: typing.Optional[str]
    voorleestitel: typing.Optional[str]


class CoachCrowdForecast(NSData):
    paddingLeft: int
    width: int
    classification: str


class Coordinate(NSData):
    lat: float
    lng: float


class Departure(NSData):
    direction: typing.Optional[str]
    name: str
    plannedDateTime: typing.Optional[datetime.datetime]
    plannedTimeZoneOffset: typing.Optional[int]
    actualDateTime: typing.Optional[datetime.datetime]
    actualTimeZoneOffset: typing.Optional[int]
    plannedTrack: typing.Optional[str]
    actualTrack: typing.Optional[str]
    product: "Product"
    trainCategory: str
    cancelled: bool
    journeyDetailRef: typing.Optional[str]
    routeStations: list["RouteStation"]
    messages: list["Message"]
    departureStatus: str


class DeparturesPayload(NSData):
    source: str
    departures: list["Departure"]


class Download(NSData):
    title: typing.Optional[str]
    url: typing.Optional[str]
    contentLength: int
    mimeType: typing.Optional[str]
    lastModified: typing.Optional[datetime.datetime]


class Eco(NSData):
    co2kg: float


class EticketNotBuyableReason(NSData):
    reason: str
    description: typing.Optional[str]


class FareLeg(NSData):
    origin: "TripOriginDestination"
    destination: "TripOriginDestination"
    operator: typing.Optional[str]
    productTypes: list[str]
    fares: list["TripTravelFare"]


class FareLegStop(NSData):
    varCode: int
    name: typing.Optional[str]


class FareRoute(NSData):
    routeId: typing.Optional[str]
    origin: "FareLegStop"
    destination: "FareLegStop"


class InternationalPrice(NSData):
    priceInCents: int
    priceInCentsExcludingSupplement: int
    product: str
    travelClass: str
    link: typing.Optional[str]


class Journey(NSData):
    notes: list["Note"]
    productNumbers: list[str]
    stops: list["JourneyStop"]
    allowCrowdReporting: bool
    source: str


class JourneyDetailLink(NSData):
    type: str
    link: "Link"


class JourneyRegistrationParameters(NSData):
    url: typing.Optional[str]
    searchUrl: str
    status: str
    bicycleReservationRequired: bool
    availability: typing.Optional["RegistrationAvailability"]


class JourneyStop(NSData):
    id: str
    stop: "Station"
    previousStopId: list[str]
    nextStopId: list[str]
    destination: typing.Optional[str]
    status: typing.Optional[str]
    kind: typing.Optional[str]
    arrivals: list["ArrivalOrDeparture"]
    departures: list["ArrivalOrDeparture"]
    actualStock: typing.Optional["Stock"]
    plannedStock: typing.Optional["Stock"]
    platformFeatures: typing.Optional[list["PlatformFeature"]]
    coachCrowdForecast: typing.Optional[list["CoachCrowdForecast"]]


class Leg(NSData):
    idx: typing.Optional[str]
    name: typing.Optional[str]
    travelType: typing.Optional[str]
    direction: typing.Optional[str]
    cancelled: bool
    changePossible: bool
    alternativeTransport: bool
    journeyDetailRef: typing.Optional[str]
    origin: "TripOriginDestination"
    destination: "TripOriginDestination"
    product: typing.Optional["Product"]
    sharedModality: typing.Optional["SharedModality"]
    notes: typing.Optional[list["Note"]]
    messages: typing.Optional[list["Message"]]
    stops: list["Stop"]
    steps: typing.Optional[list["Step"]]
    coordinates: typing.Optional[list["array"]]
    crowdForecast: typing.Optional[str]
    punctuality: typing.Optional[float]
    crossPlatformTransfer: typing.Optional[bool]
    shorterStock: typing.Optional[bool]
    changeCouldBePossible: typing.Optional[bool]
    shorterStockWarning: typing.Optional[str]
    shorterStockClassification: typing.Optional[str]
    journeyDetail: typing.Optional[list["JourneyDetailLink"]]
    reachable: bool
    plannedDurationInMinutes: typing.Optional[int]
    travelAssistanceDeparture: typing.Optional["ServiceBookingInfo"]
    travelAssistanceArrival: typing.Optional["ServiceBookingInfo"]
    overviewPolyLine: typing.Optional[list["Coordinate"]]


class Link(NSData):
    title: typing.Optional[str]
    url: typing.Optional[str]

    def __post_init__(self, data):
        if self.url is None and 'uri' in data:
            self.url = data.pop('uri')


class Location(NSData):
    station: "StationReference"  # Gives information about the station the alternative transport belongs to
    description: str  # Human readable description of the location of the alternative transport


class MeetingPointDetails(NSData):
    name: str
    minutesBefore: int


class Message(NSData):
    id: typing.Optional[str]
    externalId: typing.Optional[str]
    head: typing.Optional[str]
    text: typing.Optional[str]
    lead: typing.Optional[str]
    routeIdxFrom: typing.Optional[int]
    routeIdxTo: typing.Optional[int]
    type: typing.Optional[str]
    nesColor: typing.Optional["NesColor"]
    startDate: typing.Optional[str]
    endDate: typing.Optional[str]
    startTime: typing.Optional[str]
    endTime: typing.Optional[str]


class NearbyMeLocationId(NSData):
    value: str
    type: str


class NesColor(NSData):
    type: str
    color: str


class Note(NSData):
    value: typing.Optional[str]
    key: typing.Optional[str]
    noteType: typing.Optional[str]
    priority: typing.Optional[int]
    routeIdxFrom: typing.Optional[int]
    routeIdxTo: typing.Optional[int]
    link: typing.Optional["Link"]
    isPresentationRequired: bool
    category: typing.Optional[str]


class Part(NSData):
    stockIdentifier: typing.Optional[str]
    destination: typing.Optional["Station"]
    facilities: list[str]
    image: typing.Optional["StockPartLink"]


class PlatformFeature(NSData):
    paddingLeft: int
    width: int
    type: str
    description: str


class PrimaryMessage(NSData):
    title: str
    nesColor: "NesColor"
    message: typing.Optional["Message"]
    icon: str


class Product(NSData):
    number: typing.Optional[str]
    categoryCode: typing.Optional[str]
    shortCategoryName: typing.Optional[str]
    longCategoryName: typing.Optional[str]
    operatorCode: typing.Optional[str]
    operatorName: typing.Optional[str]
    operatorAdministrativeCode: typing.Optional[int]
    type: str
    displayName: typing.Optional[str]


class RegistrationAvailability(NSData):
    seats: bool
    numberOfSeats: typing.Optional[int]
    bicycle: bool
    numberOfBicyclePlaces: typing.Optional[int]


class RepresentationResponseArrivalsPayload(NSData):
    payload: "ArrivalsPayload"
    links: typing.Optional["object"]
    meta: typing.Optional["object"]


class RepresentationResponseDeparturesPayload(NSData):
    payload: "DeparturesPayload"
    links: typing.Optional["object"]
    meta: typing.Optional["object"]


class RepresentationResponseInternationalPrice(NSData):
    payload: "InternationalPrice"
    links: typing.Optional["object"]
    meta: typing.Optional["object"]


class RepresentationResponseJourney(NSData):
    payload: "Journey"
    links: typing.Optional["object"]
    meta: typing.Optional["object"]


class RouteStation(NSData):
    uicCode: typing.Optional[str]
    mediumName: typing.Optional[str]


class SalesOption(NSData):
    type: str
    permilleFullTariff: typing.Optional[int]
    priceInCents: typing.Optional[int]
    betterOption: bool
    recommendationText: typing.Optional[str]


class ServiceBookingInfo(NSData):
    name: str
    tripLegIndex: str
    stationUic: typing.Optional[str]
    serviceTypeIds: list[str]
    defaultAssistanceValue: bool
    canChangeAssistance: bool
    message: typing.Optional[str]


class SharedModality(NSData):
    provider: str
    name: typing.Optional[str]
    availability: bool
    nearByMeMapping: str
    planIcon: typing.Optional[str]


class Station(NSData):
    UICCode: str
    stationType: str
    EVACode: typing.Optional[str]
    code: typing.Optional[str]
    sporen: list["Track"]
    synoniemen: list[str]
    heeftFaciliteiten: bool
    heeftVertrektijden: bool
    heeftReisassistentie: bool
    namen: typing.Optional["StationsNamen"]
    land: typing.Optional[str]
    lat: typing.Optional[float]
    lng: typing.Optional[float]
    radius: typing.Optional[int]
    naderenRadius: typing.Optional[int]
    distance: typing.Optional[float]
    ingangsDatum: typing.Optional[datetime.date]
    eindDatum: typing.Optional[datetime.date]
    nearbyMeLocationId: typing.Optional["NearbyMeLocationId"]

    def __post_init__(self, data):
        if self.namen is None and 'name' in data:
            name = data.pop('name')
            self.namen = StationsNamen(kort=name, middel=name, lang=name)
        if self.land is None and 'countrycode' in data:
            self.land = data.pop('countrycode')


class StationReference(NSData):
    uicCode: str
    stationCode: typing.Optional[str]
    name: str
    coordinate: typing.Optional["Coordinate"]
    countryCode: str


class StationResponse(NSData):
    payload: list["Station"]
    links: typing.Optional["object"]
    meta: typing.Optional["object"]


class StationsNamen(NSData):
    lang: str
    middel: str
    kort: str
    festive: typing.Optional[str]


class Step(NSData):
    distanceInMeters: int
    durationInSeconds: int
    startLocation: "Location"  # Gives more information about the location of the alternative transport
    endLocation: "Location"  # Gives more information about the location of the alternative transport
    instructions: str


class Stock(NSData):
    trainType: typing.Optional[str]
    numberOfSeats: int
    numberOfParts: int
    trainParts: list["Part"]
    hasSignificantChange: bool


class StockPartLink(NSData):
    uri: str


class Stop(NSData):
    uicCode: typing.Optional[str]
    name: typing.Optional[str]
    lat: typing.Optional[float]
    lng: typing.Optional[float]
    countryCode: typing.Optional[str]
    notes: list["StopNote"]
    routeIdx: typing.Optional[int]
    departurePrognosisType: typing.Optional[str]
    plannedDepartureDateTime: typing.Optional[datetime.datetime]
    plannedDepartureTimeZoneOffset: typing.Optional[int]
    actualDepartureDateTime: typing.Optional[datetime.datetime]
    actualDepartureTimeZoneOffset: typing.Optional[int]
    plannedArrivalDateTime: typing.Optional[datetime.datetime]
    plannedArrivalTimeZoneOffset: typing.Optional[int]
    actualArrivalDateTime: typing.Optional[datetime.datetime]
    actualArrivalTimeZoneOffset: typing.Optional[int]
    plannedPassingDateTime: typing.Optional[datetime.datetime]
    actualPassingDateTime: typing.Optional[datetime.datetime]
    arrivalPrognosisType: typing.Optional[str]
    actualDepartureTrack: typing.Optional[str]
    plannedDepartureTrack: typing.Optional[str]
    plannedArrivalTrack: typing.Optional[str]
    actualArrivalTrack: typing.Optional[str]
    departureDelayInSeconds: typing.Optional[int]
    arrivalDelayInSeconds: typing.Optional[int]
    cancelled: bool
    borderStop: bool
    passing: bool
    quayCode: typing.Optional[str]


class StopNote(NSData):
    value: str
    key: typing.Optional[str]
    type: str
    priority: typing.Optional[int]


class Track(NSData):
    spoorNummer: str


class TravelAdvice(NSData):
    source: str  # Source system that has generated these travel advices
    trips: list["Trip"]  # List of trips
    scrollRequestBackwardContext: typing.Optional[str]  # Scroll context to use when scrolling back in time. Can be used in scrollContext query parameter
    scrollRequestForwardContext: typing.Optional[str]  # Scroll context to use when scrolling forward in time. Can be used in scrollContext query parameter
    message: typing.Optional[str]  # Optional message indicating why the list of trips is empty.


class TravelAssistanceInfo(NSData):
    termsAndConditionsLink: typing.Optional[str]
    tripRequestId: int
    isAssistanceRequired: bool


class Trip(NSData):
    uid: str  # Unique identifier for this trip
    ctxRecon: str  # Reconstruction context for this trip. Can be used to reconstruct this exact trip with the v3/trips/trip endpoint
    plannedDurationInMinutes: typing.Optional[int]  # Planned duration of this trip in minutes
    actualDurationInMinutes: typing.Optional[int]  # Actual duration of this trip in minutes, or the planned duration if no realtime information about this trip is available.
    transfers: int  # Number of public transit transfers
    status: str  # Status of this trip
    primaryMessage: typing.Optional["PrimaryMessage"]  # Most important message to display
    messages: typing.Optional[list["Message"]]  # List of messages regarding maintenance or disruption that influences this trip.
    legs: list["Leg"]
    overviewPolyLine: typing.Optional[list["Coordinate"]]
    crowdForecast: typing.Optional[str]
    punctuality: typing.Optional[float]
    optimal: bool  # Whether or not this trip is regarded the best possible option of all returned trips
    fareRoute: typing.Optional["FareRoute"]
    fares: typing.Optional[list["TripSalesFare"]]
    fareLegs: typing.Optional[list["FareLeg"]]
    productFare: typing.Optional["TripTravelFare"]
    fareOptions: typing.Optional["TripFareOptions"]
    bookingUrl: typing.Optional["Link"]
    type: str
    shareUrl: typing.Optional["Link"]
    realtime: bool
    travelAssistanceInfo: typing.Optional["TravelAssistanceInfo"]
    routeId: typing.Optional[str]
    registerJourney: typing.Optional["JourneyRegistrationParameters"]
    eco: typing.Optional["Eco"]


class TripFareOptions(NSData):
    isInternationalBookable: bool
    isInternational: bool
    isEticketBuyable: bool
    isPossibleWithOvChipkaart: bool
    isTotalPriceUnknown: bool
    supplementsBasedOnSelectedFare: typing.Optional[list["TripFareSupplement"]]
    reasonEticketNotBuyable: typing.Optional["EticketNotBuyableReason"]
    salesOptions: typing.Optional[list["SalesOption"]]


class TripFareSupplement(NSData):
    supplementPriceInCents: int
    legIdx: typing.Optional[str]
    fromUICCode: typing.Optional[str]
    toUICCode: typing.Optional[str]
    link: typing.Optional["Link"]


class TripOriginDestination(NSData):
    name: typing.Optional[str]
    lng: typing.Optional[float]
    lat: typing.Optional[float]
    city: typing.Optional[str]
    countryCode: typing.Optional[str]
    uicCode: typing.Optional[str]
    type: typing.Optional[str]
    prognosisType: typing.Optional[str]
    plannedTimeZoneOffset: typing.Optional[int]
    plannedDateTime: typing.Optional[datetime.datetime]
    actualTimeZoneOffset: typing.Optional[int]
    actualDateTime: typing.Optional[datetime.datetime]
    plannedTrack: typing.Optional[str]
    actualTrack: typing.Optional[str]
    exitSide: typing.Optional[str]
    checkinStatus: typing.Optional[str]
    travelAssistanceBookingInfo: typing.Optional["ServiceBookingInfo"]
    travelAssistanceMeetingPoints: typing.Optional[list[str]]
    travelAssistanceMeetingPointDetails: typing.Optional[list["MeetingPointDetails"]]
    notes: typing.Optional[list["Note"]]
    quayCode: typing.Optional[str]


class TripSalesFare(NSData):
    priceInCents: typing.Optional[int]
    product: typing.Optional[str]
    travelClass: typing.Optional[str]
    priceInCentsExcludingSupplement: typing.Optional[int]
    discountType: typing.Optional[str]
    supplementInCents: typing.Optional[int]
    link: typing.Optional[str]


class TripTravelFare(NSData):
    priceInCents: typing.Optional[int]
    priceInCentsExcludingSupplement: typing.Optional[int]
    supplementInCents: typing.Optional[int]
    buyableTicketPriceInCents: typing.Optional[int]
    buyableTicketPriceInCentsExcludingSupplement: typing.Optional[int]
    buyableTicketSupplementPriceInCents: typing.Optional[int]
    product: typing.Optional[str]
    travelClass: typing.Optional[str]
    discountType: str
    link: typing.Optional[str]
