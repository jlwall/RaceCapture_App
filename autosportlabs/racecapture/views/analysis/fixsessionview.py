import os
from threading import Thread
import kivy
kivy.require('1.9.1')
from kivy.app import Builder
from kivy.logger import Logger
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup
from kivy.metrics import dp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.listview import ListView, ListItemButton
from kivy.uix.screenmanager import Screen
from utils import kvFind
from kivy.adapters.listadapter import ListAdapter
from autosportlabs.uix.button.featurebutton import FeatureButton
from autosportlabs.uix.textwidget import FieldInput
from autosportlabs.racecapture.views.util.alertview import alertPopup
from autosportlabs.racecapture.views.file.loaddialogview import LoadDialog
from autosportlabs.racecapture.views.file.savedialogview import SaveDialog
from iconbutton import IconButton
from fieldlabel import FieldLabel

Builder.load_file('autosportlabs/racecapture/views/analysis/fixsessionview.kv')


class FixSessionView(BoxLayout):

    def __init__(self, session_id, settings, datastore, **kwargs):
        super(FixSessionView, self).__init__(**kwargs)
        self.session_id = session_id
        self._datastore = datastore

