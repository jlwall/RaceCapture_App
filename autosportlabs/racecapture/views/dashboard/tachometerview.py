import kivy
kivy.require('1.9.1')
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.app import Builder
from kivy.clock import Clock
from autosportlabs.racecapture.views.dashboard.widgets.tachometer import TachometerGauge
from autosportlabs.racecapture.views.dashboard.widgets.bignumberview import BigNumberView
from autosportlabs.racecapture.views.dashboard.widgets.laptime import Laptime
from autosportlabs.racecapture.views.dashboard.widgets.timedelta import TimeDelta
from autosportlabs.racecapture.views.dashboard.widgets.gauge import Gauge
from autosportlabs.racecapture.views.dashboard.dashboardscreen import DashboardScreen
from utils import kvFind, kvFindClass

class TachometerView(DashboardScreen):
    Builder.load_file('autosportlabs/racecapture/views/dashboard/tachometerview.kv')

    _databus = None
    _settings = None

    def __init__(self, databus, settings, **kwargs):
        super(TachometerView, self).__init__(**kwargs)
        self._databus = databus
        self._settings = settings
        self._initialized = False

    def on_meta(self, channelMetas):
        pass

    def on_enter(self):
        if self._initialized == False:
            self._init_screen()

    def _init_screen(self):
        dataBus = self._databus
        settings = self._settings
        dataBus.addMetaListener(self.on_meta)

        gauges = list(kvFindClass(self, Gauge))

        for gauge in gauges:
            gauge.settings = settings
            gauge.data_bus = dataBus

        self._initialized = True

