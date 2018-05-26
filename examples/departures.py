import ns_api as ns
import pickle

if __name__ == '__main__':
    with open('credentials.pkl', 'rb') as f:
        user, passwd = pickle.load(f)
    api = ns.NSAPI(user, passwd)
    departures = api.get_departures('geldermalsen')
    for d in departures:
        base = 'The {} to {}'.format(d.train_type, d.destination)
        delay = ' has a delay of {:d} {}'.format(d.departure_delay, 'minute' if d.departure_delay == 1 else 'minutes') \
            if d.departure_delay else ' is on time'
        time = ', and departs at {}'.format(d.departure_time.strftime('%H:%M'))
        track = ' from track {}'.format(d.departure_track) if d.departure_track else ''
        print(base + delay + time + track)
        if d.journy_hint:
            for line in d.journy_hint.splitlines():
                print('-  {}'.format(line))
        if d.remarks:
            for line in d.remarks.splitlines():
                print('!  {}'.format(line))
