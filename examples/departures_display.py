import threading
import ns_api as ns
import pickle
import sys
import time
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QFontMetrics
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtWidgets import QVBoxLayout, QGridLayout

big_font = QFont('Times', 15, QFont.Bold)
small_font = QFont('Times', 10, QFont.Bold)
small_font_metrics = QFontMetrics(small_font)
color_blue = QPalette()
color_blue.setColor(QPalette.WindowText, Qt.darkBlue)
color_red = QPalette()
color_red.setColor(QPalette.WindowText, Qt.darkRed)
color_gray = QPalette()
color_gray.setColor(QPalette.WindowText, Qt.gray)
background_white = QPalette()
background_white.setColor(QPalette.Window, Qt.white)
background_light = QPalette()
background_light.setColor(QPalette.Window, QColor(204, 230, 255))


def big_font_label(*args, **kwargs):
    lbl = QLabel(*args, font=big_font, **kwargs)
    lbl.setPalette(color_blue)
    return lbl


def small_font_label(*args, **kwargs):
    lbl = QLabel(*args, font=small_font, **kwargs)
    lbl.setPalette(color_blue)
    return lbl


class DepartureWidget(QWidget):
    def __init__(self, departure: ns.Departure=None, index=0):
        QWidget.__init__(self)
        self.setFixedWidth(750)
        self.departure = departure
        self.layout = QGridLayout(self)
        self.setAutoFillBackground(True)
        self.setPalette(background_white if index % 2 else background_light)

        self.time = big_font_label()
        self.time.setFixedWidth(70)
        self.delay = small_font_label()
        self.delay.setPalette(color_red)
        self.destination = big_font_label()
        self.route = small_font_label()
        self.track = big_font_label()
        self.track.setFixedWidth(50)
        self.carrier = small_font_label()
        self.carrier.setFixedWidth(170)

        self.layout.addWidget(self.time, 0, 0)
        self.layout.addWidget(self.delay, 1, 0)
        self.layout.addWidget(self.destination, 0, 1)
        self.layout.addWidget(self.route, 1, 1)
        self.layout.addWidget(self.track, 0, 2, 2, 1)
        self.layout.addWidget(self.carrier, 0, 3, 2, 1)

    def update_departure(self, departure):
        if departure != self.departure:
            self.departure = departure
            self.update_information()
            self.update()

    def update_information(self):
        if self.departure is not None:
            self.time.setText(self.departure.departure_time.strftime('%H:%M'))
            self.delay.setText(self.departure.departure_delay.friendly)
            self.destination.setText(self.departure.destination)
            if self.departure.remarks:
                self.route.setText(self.departure.remarks)
                self.route.setPalette(color_red)
            elif self.departure.journy_hint:
                self.route.setText(self.departure.journy_hint)
                self.route.setPalette(color_red)
            else:
                self.route.setText('via ' + self.departure.route if self.departure.route else '')
                self.route.setPalette(color_blue)
            self.track.setText(self.departure.departure_track.upper())
            self.track.setPalette(color_red if self.departure.departure_track.changed else color_blue)
            carrier = str(self.departure.carrier) if self.departure.carrier is not ns.Carrier.UNKNOWN else ''
            train = str(self.departure.train_type) if self.departure.train_type is not ns.Train.UNKNOWN else ''
            sep = '\n' if small_font_metrics.width(carrier + ' ' + train) > self.carrier.width() else ' '
            self.carrier.setText(carrier + sep + train)
            if self.departure.remarks and 'Rijdt vandaag niet' in self.departure.remarks:
                self.foreach_widget(lambda elm: elm.setPalette(color_gray), [self.route])
            else:
                self.foreach_widget(lambda elm: elm.setPalette(color_blue), [self.route])
        else:
            self.foreach_widget(lambda elm: elm.setText(''))

    def foreach_widget(self, func, not_elms=None):
        for elm in (self.time, self.delay, self.destination, self.route, self.track, self.carrier):
            if not_elms is None or elm not in not_elms:
                func(elm)


class DepartureDisplay(QWidget):
    new_departures = pyqtSignal(object)

    def __init__(self, api: ns.NSAPI, station: str):
        QWidget.__init__(self)
        self.api = api
        self.station = station
        self.setWindowTitle('Departures for ' + station)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.setPalette(background_white)

        self.n_departures = 10
        self.departure_widgets = []
        for n in range(self.n_departures):
            dep_widget = DepartureWidget(index=n)
            self.departure_widgets.append(dep_widget)
            self.layout.addWidget(dep_widget)
        self.new_departures.connect(self.update_departures)
        self.departures = []
        self.running = True
        self.update_time = 5
        threading.Thread(target=self.update_worker).start()

    def closeEvent(self, ev):
        self.running = False

    def update_worker(self):
        while self.running:
            try:
                departures = self.api.get_departures(self.station)[:self.n_departures]
                departures.extend([None for n in range(self.n_departures-len(departures))])
            except:
                departures = [None for n in range(self.n_departures)]
            if departures != self.departures:
                self.new_departures.emit(departures)
                self.departures = departures
            time.sleep(self.update_time)

    def update_departures(self, departures):
        for widget, departure in zip(self.departure_widgets, departures):
            widget.update_departure(departure)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    with open('credentials.pkl', 'rb') as f:
        usr,pwd = pickle.load(f)
    api = ns.NSAPI(usr, pwd)
    sign = DepartureDisplay(api, 'Geldermalsen')
    sign.show()
    return_code = app.exec_()
    sys.exit(return_code)
