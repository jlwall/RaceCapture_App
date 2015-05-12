import kivy
kivy.require('1.8.0')
from kivy.app import Builder
from kivy.uix.anchorlayout import AnchorLayout
from iconbutton import IconButton
from autosportlabs.racecapture.views.channels.channelselectview import ChannelSelectView
from autosportlabs.racecapture.views.analysis.customizechannelsview import CustomizeChannelsView
from kivy.uix.popup import Popup
Builder.load_file('autosportlabs/racecapture/views/analysis/analysiswidget.kv')

class AnalysisWidget(AnchorLayout):
    settings = None
    datastore = None
    def __init__(self, **kwargs):
        super(AnalysisWidget, self).__init__(**kwargs)
        self.settings = kwargs.get('settings')
        self.datastore = kwargs.get('datastore')
    
    def on_options(self, *args):
        pass    

class ChannelAnalysisWidget(AnalysisWidget):
    _popup = None
    def __init__(self, **kwargs):
        super(ChannelAnalysisWidget, self).__init__(**kwargs)
        self.register_event_type('on_channel_selected')
    
    def on_channel_selected(self, value):
        pass
    
    def on_options(self, *args):
        self.showCustomizeDialog()
        
    def showCustomizeDialog(self):
        content = CustomizeChannelsView(settings=self.settings, datastore=self.datastore)
        content.bind(on_channels_customized=self.channels_customized)

        popup = Popup(title="Customize Channels", content=content, size_hint=(0.7, 0.7))
        popup.bind(on_dismiss=self.popup_dismissed)
        popup.open()
        self._popup = popup
    
    def channels_customized(self, *args):
        print("channels customized")
#        self.dispatch('on_channel_selected', value)
        self._dismiss_popup()

    def popup_dismissed(self, *args):
        self._popup = None
        
    def _dismiss_popup(self, *args):
        if self._popup:
            self._popup.dismiss()
            self._popup = None
    