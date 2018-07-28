import socket
import logging
import threading
from nsapi import NSAPI

from zeroconf import ServiceBrowser, Zeroconf, ServiceInfo
import zmq

logger = logging.getLogger(__name__)


class DepartureService(NSAPI):
    BROADCAST_PORT = 4191

    def __init__(self, stype, cluster_name, cluster_index, usr=None, passwd=None):
        if cluster_index == 0:
            if usr is None or passwd is None:
                raise ValueError('The first node should have an api username and password')
            NSAPI.__init__(self, usr, passwd)
        else:
            NSAPI.__init__(self, '', '')

        self.stype = stype                      # Service type (_nsdeps._tcp.local.)
        self.cluster_name = cluster_name        # Cluster name
        self.cluster_index = cluster_index      # Cluster index
        self.zeroconf = Zeroconf()
        self.browser = ServiceBrowser(self.zeroconf, stype, self)
        self.displays = []
        self.parent_ip = None
        self.zmq_context = zmq.Context.instance()
        self.zmq_out = zmq.Socket(zmq.PUB)
        self.zmq_out.bind('tcp://{}:{}'.format('*', self.BROADCAST_PORT))
        if self.cluster_index > 0:
            self.zmq_in = zmq.Socket(zmq.SUB)
            self.zmq_in_poller = None
            self.zmq_in_connected = False
        self.running = True
        threading.Thread(target=self.receive_worker).start()

    def remove_service(self, zeroconf, stype, sname):
        same_service = [s for s in self.displays if s.type == stype and s.name == sname]
        if same_service:
            del self.displays[self.displays.index(same_service[0])]
        self.displays_changed()

    def add_service(self, zeroconf, stype, sname):
        info = zeroconf.get_service_info(stype, sname)
        if info is None:
            return
        same_service = [s for s in self.displays if s.type == stype and s.name == sname]
        if same_service:
            self.displays[self.displays.index(same_service[0])] = info
        else:
            self.displays.append(info)
        self.displays_changed()

    def displays_changed(self):
        for disp in self.displays:
            try:
                properties = {k.decode(): v.decode() for k, v in disp.properties.items()}
                if properties.get('cluster') == self.cluster_name \
                        and properties.get('index') == str(self.cluster_index-1) \
                        and disp.address:
                    parent_ip = '.'.join([str(c) for c in disp.address])
                    if parent_ip != self.parent_ip:
                        self.parent_ip_changed(parent_ip)
            except Exception as e:
                logger.error(e)

    def parent_ip_changed(self, ip):
        if self.parent_ip is not None:
            return                      # Don't dynamically switch parent hosts
        self.parent_ip = ip
        self.zmq_in.connect('tcp://{}:{}'.format(self.parent_ip, self.BROADCAST_PORT))
        self.zmq_in.setsockopt_string(zmq.SUBSCRIBE, '')
        self.zmq_in_poller = zmq.Poller()
        self.zmq_in_poller.register(self.zmq_in, zmq.POLLIN)
        self.zmq_in_connected = True

    def receive_worker(self):
        while self.running:
            if self.cluster_index == 0:
                data = self.get_departures(self.statio)
            else:
                if self.zmq_in_connected:
                    evnts = dict(self.zmq_in_poller.poll(1000))
                    if evnts:
                        data = self.zmq_in.recv_string()



if __name__ == '__main__':
    service = DepartureService('_nsdeps._tcp.local.', 'entrance', 2)
    input()
    pass
