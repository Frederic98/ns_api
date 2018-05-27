from enum import Enum


class nsEnum(Enum):
    @classmethod
    def _missing_(cls, value):
        return cls.UNKNOWN

    def __format__(self, format_spec):
        return self.value.__format__(format_spec)

    def __str__(self):
        return self.value.__str__()


class Train(nsEnum):
    INTERCITY = 'Intercity'
    INTERCITY_DIRECT = 'Intercity direct'
    SPRINTER = 'Sprinter'
    STOPTRAIN = 'stoptrein'
    ICE_INTERNATIONAL = 'ICE International'
    THALYS = 'Thalys'
    STOPBUS = 'Stopbus i.p.v. trein'
    UNKNOWN = 'Unknown'


class Carrier(nsEnum):
    NS = 'NS'
    NS_INTERNATIONAL = 'NS International'
    ARRIVA = 'Arriva'
    BLAUWNET = 'Blauwnet'
    UNKNOWN = 'Unknown'


class StationType(nsEnum):
    NODE_INTERCITY = 'knooppuntIntercitystation'
    INTERCITY = 'intercitystation'
    NODE_STOPTRAIN = 'knooppuntStoptreinstation'
    STOPTRAIN = 'stoptreinstation'
    MEGA = 'megastation'
    OPTIONAL = 'facultatiefStation'
    SPEEDTRAIN = 'sneltreinstation'
    NODE_SPEEDTRAIN = 'knooppuntSneltreinstation'
    UNKNOWN = 'station'


class StationCountry(nsEnum):
    NETHERLANDS = 'NL'
    GERMANY = 'D'
    BELGIUM = 'B'
    FRANCE = 'F'
    ITALY = 'I'
    GREAT_BRITTAIN = 'GB'
    SWITZERLAND = 'CH'
    AUSTRIA = 'A'
    HUNGARY = 'H'
    CZECH = 'CZ'
    POLAND = 'PL'
    UNKNOWN = ''


class Status(nsEnum):
    ON_SCHEDULE = 'VOLGENS-PLAN'
    CHANGED = 'GEWIJZIGD'
    DELAYED = 'VERTRAAGD'
    NEW = 'NIEUW'
    NOT_OPTIMAL = 'NIET-OPTIMAAL'
    NOT_POSSIBLE = 'NIET-MOGELIJK'
    PLAN_CHANGED = 'PLAN-GEWIJZIGD'

    # Some statuses only for journey-parts
    # ON_SCHEDULE = 'VOLGENS-PLAN'
    CANCELLED = 'GEANNULEERD'       # (=cancelled train)
    # CHANGED = 'GEWIJZIGD'         # (=change to the plan on the day itself)
    TRANSFER_NOT_POSSIBLE = 'OVERSTAP-NIET-MOGELIJK'
    # DELAYED = 'VERTRAAGD'
    # NEW = 'NIEUW'                 # (=extra train)

    UNKNOWN = 'Unknown'
