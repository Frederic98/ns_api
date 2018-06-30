#!/usr/bin/env python3
import threading
from _weakrefset import WeakSet
import nsapi as ns
import pickle
import sys
import time
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor, QFontMetrics, QResizeEvent, QKeyEvent, QCloseEvent
from PyQt5.QtWidgets import QApplication, QWidget, QLabel
from PyQt5.QtWidgets import QVBoxLayout, QGridLayout

big_font = QFont('Times', 40, QFont.Bold)
small_font = QFont('Times', 25, QFont.Bold)
big_font_metrics = QFontMetrics(big_font)
small_font_metrics = QFontMetrics(small_font)
big_fonts = WeakSet()
small_fonts = WeakSet()
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
    big_fonts.add(lbl)
    return lbl


def small_font_label(*args, **kwargs):
    lbl = QLabel(*args, font=small_font, **kwargs)
    lbl.setPalette(color_blue)
    small_fonts.add(lbl)
    return lbl


class DepartureWidget(QWidget):
    def __init__(self, departure: ns.Departure=None, index=0):
        QWidget.__init__(self)
        # self.setFixedWidth(750)
        self.departure = departure
        self.layout = QGridLayout(self)
        self.setAutoFillBackground(True)
        self.setPalette(background_white if index % 2 else background_light)
        self.canceled = False

        self.time = big_font_label()
        self.delay = small_font_label()
        self.delay.setPalette(color_red)
        self.destination = big_font_label()
        self.route = small_font_label()
        self.track = big_font_label()
        self.carrier = small_font_label()

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
            self.canceled = self.departure.remarks and 'Rijdt vandaag niet' in self.departure.remarks

            self.time.setText(self.departure.departure_time.strftime('%H:%M'))
            self.set_colorhint(self.time, color_blue)
            self.delay.setText(self.departure.departure_delay.friendly)
            self.set_colorhint(self.delay, color_red)
            self.destination.setText(self.departure.destination)
            self.set_colorhint(self.destination, color_blue)
            if self.departure.remarks:
                self.route.setText(self.departure.remarks)
                self.route.setPalette(color_red)
            elif self.departure.journy_hint:
                self.route.setText(self.departure.journy_hint)
                self.set_colorhint(self.route, color_red)
            else:
                self.route.setText('via ' + self.departure.route if self.departure.route else '')
                self.set_colorhint(self.route, color_blue)
            self.track.setText(self.departure.departure_track.upper())
            self.set_colorhint(self.track, color_red if self.departure.departure_track.changed else color_blue)
            carrier = str(self.departure.carrier) if self.departure.carrier is not ns.Carrier.UNKNOWN else ''
            train = str(self.departure.train_type) if self.departure.train_type is not ns.Train.UNKNOWN else ''
            sep = '\n' if small_font_metrics.width(carrier + ' ' + train) > self.carrier.width() else ' '
            self.carrier.setText(carrier + sep + train)
            self.set_colorhint(self.carrier, color_blue)
        else:
            for elm in (self.time, self.delay, self.destination, self.route, self.track, self.carrier):
                elm.setText('')

    def set_colorhint(self, widget: QWidget, color):
        widget.setPalette(color_gray if self.canceled else color)

    def recalc_widths(self):
        self.time.setFixedWidth(big_font_metrics.width('00:00')*1.1)
        self.track.setFixedWidth(big_font_metrics.width('XXX')*1.1)
        self.carrier.setFixedWidth(small_font_metrics.width('X'*12))


class DepartureDisplay(QWidget):
    new_departures = pyqtSignal(object)

    def __init__(self, api: ns.NSAPI, station: str,
                 fullscreen=False, n_departures=8):
        QWidget.__init__(self)
        self.api = api
        self.station = station
        self.setWindowTitle('Departures for ' + station)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0,0,0,0)
        self.layout.setSpacing(0)
        self.setPalette(background_white)

        self.n_departures = n_departures
        self.departure_widgets = []
        for n in range(self.n_departures):
            dep_widget = DepartureWidget(index=n)
            self.departure_widgets.append(dep_widget)
            self.layout.addWidget(dep_widget)
        self.new_departures.connect(self.update_departures)
        self.departures = []
        self.stop_event = threading.Event()
        self.update_time = 5
        threading.Thread(target=self.update_worker).start()

        if fullscreen:
            self.setWindowState(Qt.WindowFullScreen)
        else:
            screensize = QApplication.primaryScreen().size()
            self.resize(screensize.width()*0.7, screensize.height()*0.7)

    def update_worker(self):
        while not self.stop_event.is_set():
            try:
                departures = self.api.get_departures(self.station)[:self.n_departures]
                departures.extend([None for n in range(self.n_departures-len(departures))])
            except:
                departures = [None for n in range(self.n_departures)]
            if departures != self.departures:
                self.new_departures.emit(departures)
                self.departures = departures
            self.stop_event.wait(5)

    def update_departures(self, departures):
        for widget, departure in zip(self.departure_widgets, departures):
            widget.update_departure(departure)

    def resizeEvent(self, evnt: QResizeEvent):
        new_width = evnt.size().width()
        if not self.isFullScreen():
            self.resize(new_width, 30)
        big_font.setPointSize(new_width * 40/1920)
        small_font.setPointSize(new_width * 25/1920)
        global big_font_metrics
        global small_font_metrics
        big_font_metrics = QFontMetrics(big_font)
        small_font_metrics = QFontMetrics(small_font)
        for lbl in big_fonts:
            lbl.setFont(big_font)
        for lbl in small_fonts:
            lbl.setFont(small_font)
        for depw in self.departure_widgets:
            depw.recalc_widths()
        self.update()

    def keyPressEvent(self, evnt: QKeyEvent):
        if evnt.key() == Qt.Key_Escape:
            self.stop_event.set()
            QApplication.instance().exit(0)

    def closeEvent(self, evnt: QCloseEvent):
        self.stop_event.set()


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Run NS departures display')
    parser.add_argument('-f', action='store_true', dest='fullscreen',
                        help='run in full-screen mode')
    parser.add_argument('-n', dest='n_departures', metavar='NUM', type=int, default=7,
                        help='number of departures to display')
    parser.add_argument('station', help='the station of which to display the departures')
    args = parser.parse_args()
    app = QApplication(sys.argv)
    with open('credentials.pkl', 'rb') as f:
        usr, pwd = pickle.load(f)
    api = ns.NSAPI(usr, pwd)
    sign = DepartureDisplay(api, args.station, args.fullscreen, args.n_departures)
    sign.show()
    return_code = app.exec_()
    sys.exit(return_code)
