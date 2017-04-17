#
# Race Capture App
#
# Copyright (C) 2014-2016 Autosport Labs
#
# This file is part of the Race Capture App
#
# This is free software: you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This software is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the GNU General Public License for more details. You should
# have received a copy of the GNU General Public License along with
# this code. If not, see <http://www.gnu.org/licenses/>.

import kivy
kivy.require('1.9.1')

from kivy.uix.boxlayout import BoxLayout
from kivy.uix.accordion import Accordion, AccordionItem
from kivy.uix.spinner import Spinner
from kivy.app import Builder
from mappedspinner import MappedSpinner
from utils import *
from kivy.metrics import sp
from autosportlabs.racecapture.views.configuration.baseconfigview import BaseMultiChannelConfigView, BaseChannelView
from autosportlabs.racecapture.config.rcpconfig import *

TIMER_CHANNELS_VIEW_KV = 'autosportlabs/racecapture/views/configuration/rcp/timerchannelsview.kv'


class PulseChannelsView(BaseMultiChannelConfigView):
    Builder.load_file(TIMER_CHANNELS_VIEW_KV)

    def __init__(self, **kwargs):
        super(PulseChannelsView, self).__init__(**kwargs)
        self.channel_title = 'Timer '
        self.accordion_item_height = sp(150)

    def channel_builder(self, index, max_sample_rate):
        editor = PulseChannel(id='timer' + str(index), channels=self.channels)
        editor.bind(on_modified=self.on_modified)
        if self.config:
            editor.on_config_updated(self.config.channels[index], max_sample_rate)
        return editor

    def get_specific_config(self, rcp_cfg):
        return rcp_cfg.timerConfig


class TimerModeSpinner(MappedSpinner):
    def __init__(self, **kwargs):
        super(TimerModeSpinner, self).__init__(**kwargs)
        self.setValueMap({0:'RPM', 1:'Frequency', 2:'Period (ms)', 3:'Period (us)'}, 'RPM')

class TimerSpeedSpinner(MappedSpinner):
    def __init__(self, **kwargs):
        super(TimerSpeedSpinner, self).__init__(**kwargs)
        self.setValueMap({0:'Slow', 1:'Medium', 2:'Fast'}, 'Medium')

class PulsePerRevSpinner(MappedSpinner):
    def __init__(self, **kwargs):
        super(PulsePerRevSpinner, self).__init__(**kwargs)
        valueMap = {}
        for i in range (1, 64):
            valueMap[i] = str(i)
        self.setValueMap(valueMap, '1');

class PulseChannel(BaseChannelView):
    def __init__(self, **kwargs):
        super(PulseChannel, self).__init__(**kwargs)

    def on_alpha_map_value(self, instance, value):
        try:
            if self.channelConfig:
                if  float(value) > 1:
                    value = 1
                    self.ids.alpha.text = str(value)
                elif float(value) < 0:
                    value = 0
                    self.ids.alpha.text = str(value)
                self.channelConfig.alpha = float(value)
                self.channelConfig.stale = True
                self.dispatch('on_modified', self.channelConfig)
        except:
            pass

    def on_pulse_per_rev(self, instance, value):
        if self.channelConfig:
            self.channelConfig.pulsePerRev = int(value)
            self.channelConfig.stale = True
            self.dispatch('on_modified', self.channelConfig)

    def on_mode(self, instance, value):
        if self.channelConfig:
            self.channelConfig.mode = int(instance.getValueFromKey(value))
            self.channelConfig.stale = True
            self.dispatch('on_modified', self.channelConfig)

    def on_speed(self, instance, value):
        if self.channelConfig:
            self.channelConfig.speed = int(instance.getValueFromKey(value))
            self.channelConfig.stale = True
            self.dispatch('on_modified', self.channelConfig)

    def on_config_updated(self, channelConfig, max_sample_rate):
        self.ids.sr.setValue(channelConfig.sampleRate, max_sample_rate)

        self.ids.chan_id.setValue(channelConfig)

        self.ids.alpha.text = str(channelConfig.alpha)

        mode_spinner = kvFind(self, 'rcid', 'mode')
        mode_spinner.setFromValue(channelConfig.mode)

        speed_spinner = kvFind(self, 'rcid', 'speed')
        speed_spinner.setFromValue(channelConfig.speed)

        pulse_per_rev_spinner = kvFind(self, 'rcid', 'ppr')
        pulse_per_rev_spinner.setFromValue(channelConfig.pulsePerRev)

        self.channelConfig = channelConfig
