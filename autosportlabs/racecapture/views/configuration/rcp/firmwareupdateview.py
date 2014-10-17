import kivy
kivy.require('1.8.0')

from kivy.properties import ObjectProperty
from settingsview import SettingsMappedSpinner, SettingsSwitch
from mappedspinner import MappedSpinner
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.popup import Popup
from kivy.uix.label import Label
from kivy.app import Builder
from utils import *
from autosportlabs.racecapture.views.configuration.baseconfigview import BaseConfigView
from autosportlabs.racecapture.views.file.loaddialogview import LoadDialog
from autosportlabs.racecapture.views.util.alertview import alertPopup
from asl_f4_loader import fw_update
from time import sleep
from threading import Thread

Builder.load_file('autosportlabs/racecapture/views/configuration/rcp/firmwareupdateview.kv')

#TODO: MK1 support
class FirmwareUpdateView(BaseConfigView):
    progress_gauge = ObjectProperty(None)

    def __init__(self, **kwargs):
        self.dataBusPump = kwargs.get('dataBusPump', None)

        super(FirmwareUpdateView, self).__init__(**kwargs)
        self.register_event_type('on_config_updated')

    def on_config_updated(self, rcpCfg):
        pass

    def check_online(self):
        popup = Popup(title='Check Online',
                      content=Label(text='Coming soon!'),
                      size_hint=(None, None), size=(400, 400))
        popup.open()

    def select_file(self):
        #Inside a try block since this will fail if there is no device detected
        try:
            self.dataBusPump.rcApi.stopMessageRxWorker()
        except:
            pass
        content = LoadDialog(ok=self.update_fw, cancel=self.dismiss_popup,
                             filters=['*' + '.ihex'])
        self._popup = Popup(title="Load file", content=content, size_hint=(0.9, 0.9))
        self._popup.open()

    def _update_progress_gauge(self, percent):
        kvFind(self, 'rcid', 'fw_progress').value = int(percent)

    def _teardown_json_serial(self):
        self.dataBusPump.stopDataPump()
        self.dataBusPump.rcApi.resetDevice(bootloader=True)
        self.dataBusPump.rcApi.comms.close()
        sleep(5)

    def _restart_json_serial(self):
        self.dataBusPump.rcApi.runAutoDetect()
        self.dataBusPump.startDataPump(self.dataBusPump.dataBus,
                                       self.dataBusPump.rcApi)
                        
    def _update_thread(self, instance):
        try:
            selection = instance.selection
            filename = selection[0] if len(selection) else None
            if filename:
                #Even though we stopped the RX thread, this is OK
                #since it doesn't return a value
                try:
                    kvFind(self, 'rcid', 'fw_progress').title="Processing"
                    self._teardown_json_serial()
                except:
                    import sys, traceback
                    print "Exception in user code:"
                    print '-'*60
                    traceback.print_exc(file=sys.stdout)
                    print '-'*60
                    pass

                kvFind(self, 'rcid', 'fw_progress').title="Progress"

                #Get our firmware updater class and register the
                #callback that will update the progress gauge
                fu = fw_update.FwUpdater()
                fu.register_progress_callback(self._update_progress_gauge)

                #Find our bootloader
                port = fu.scan_for_device()

                #Bail if we can't find an active loader
                if not port:
                    kvFind(self, 'rcid', 'fw_progress').title=""
                    raise Exception("Unable to locate bootloader")

                #Go on our jolly way
                fu.update_firmware(filename, port)
                kvFind(self, 'rcid', 'fw_progress').title="Restarting"

                #Sleep for a few seconds since we need to let USB re-enumerate
                sleep(10)
            else:
                alertPopup('Error Loading', 'No firmware file selected')
        except Exception as detail:
            alertPopup('Error Loading', 'Failed to Load Firmware:\n\n' + str(detail))

        self._restart_json_serial()
        kvFind(self, 'rcid', 'fw_progress').value = 0
        kvFind(self, 'rcid', 'fw_progress').title=""



    def update_fw(self, instance):
        self._popup.dismiss()
        #The comma is necessary since we need to pass in a sequence of args
        t = Thread(target=self._update_thread, args=(instance,))
        t.daemon = True
        t.start()

    def dismiss_popup(self, *args):
        self._popup.dismiss()