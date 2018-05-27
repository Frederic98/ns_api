import ns_api as ns
import pickle

DT_FORMAT = '%d-%m-%Y %H:%M'
TIME_FORMAT = '%H:%M'


def print_journey(journey: ns.Journey):
    for notification in journey.notifications:
        print('{} {}'.format('!!' if notification.serious else '--', notification.text))
    d_plan = journey.duration_planned
    d_actual = journey.duration_actual
    if d_plan != d_actual:
        print('Planned duration: {}:{}'.format(d_plan.hours, d_plan.minutes))
        print('Actual duration: {}:{}'.format(d_actual.hours, d_actual.minutes))
    else:
        print('Duration:  {}:{}'.format(d_plan.hours, d_plan.minutes))
    print('Departure: ' + journey.departure_time_actual.strftime(DT_FORMAT))
    print('Arrival:   ' + journey.arrival_time_actual.strftime(DT_FORMAT))
    print('Number of transfers: ' + str(journey.transfers))
    for part in journey.parts:
        print(' ->' + str(part.carrier) + ' ' + str(part.train_type))
        start = part.stops[0]
        end = part.stops[-1]
        print('   ' + str(start.station) + ': track ' + start.track + ' @ ' + start.time.strftime(TIME_FORMAT))
        for stop in part.stops[1:-1]:
            print('     ' + str(stop.station))
        print('   ' + str(end.station) + ': track ' + end.track + ' @ ' + end.time.strftime(TIME_FORMAT))


if __name__ == '__main__':
    with open('credentials.pkl', 'rb') as f:
        user, passwd = pickle.load(f)
    api = ns.NSAPI(user, passwd)
    options = api.get_journey('gdm', 'amsterdam')
    optimal = [option for option in options if option.optimal][0]
    print_journey(optimal)

