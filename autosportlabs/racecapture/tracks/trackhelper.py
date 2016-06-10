from datetime import datetime
from autosportlabs.racecapture.geo.geopoint import GeoPoint
from kivy.logger import Logger
from kivy.event import EventDispatcher
from autosportlabs.racecapture.config.rcpconfig import *


class TrackHelper(EventDispatcher):
    """
    This class' responsibility is to make sure RC detects a track when it runs so
    users get lap timing when they are on track
    """

    def __init__(self, track_manager, rc_api, status_pump, rc_config, **kwargs):
        """
        Init!
        :param track_manager: TrackManager instance
        :param rc_api: RCAPI instance
        :param status_pump: StatusPump instance
        :param rc_config: RCConfig instance
        :param kwargs: kwargs
        :return: None
        """
        self.register_event_type('on_track_detected')
        super(TrackHelper, self).__init__(**kwargs)

        self.track_manager = track_manager
        self.rc_api = rc_api
        self.status_pump = status_pump
        self.rc_config = rc_config

        # Number of seconds to wait until we attempt to figure out what track we're at,
        # allows RC hardware some time to detect a track
        self._wait_period = 4

        #When RC was ready, we wait _wait_period after this to ensure RC had time to search for a track
        self._ready_start_time = None

        #Status hash from StatusPump
        self._status = None

        #Has the TrackManager loaded all tracks?
        self._tracks_loaded = False

        #Did RC detect a track?
        self._track_detected = False

        self.status_pump.add_listener(self.on_status)

        if len(self.track_manager.tracks) == 0:
            self.track_manager.load_tracks(success_cb=self._on_tracks_loaded, fail_cb=self._on_tracks_load_fail)
            Logger.info("TrackHelper: Loading tracks")
        else:
            self._tracks_loaded = True

        Logger.debug("TrackHelper: initialized")

    def on_track_detected(self):
        """
        Dispatched when track found in track db
        :return:
        """
        pass

    def on_status(self, status):
        """
        StatusPump status listener
        :param status: Status hash
        :return: None
        """
        self._status = status['status']
        self._track_detected = self._status['track']['status'] != 0

        self._check_track_detection()

    def _on_tracks_loaded(self):
        """
        Callback for when TrackManager loads tracks
        :return: None
        """
        self._tracks_loaded = True
        Logger.info("TrackHelper: tracks loaded")

    def _on_tracks_load_fail(self):
        """
        Callback for when TrackManager fails to load tracks
        :return: None
        """
        Logger.error("TrackHelper: track load failed")

    def _is_ready(self):
        """
        Determines if all preconditions for searching for a track are met
            1) RC has *not* detected a track
            2) GPS is initialized and has a quality signal
            3) We've waited a short amount of time to allow RC to search for a track
            4) TrackManager has loaded tracks
            5) RC config has tracks
        :return: Boolean
        """
        if self._track_detected:
            Logger.info("TrackHelper: track detected, aborting")
            return False

        if self._status['GPS']['init'] != 1 and self._status['GPS']['qual'] < 2:
            Logger.info("TrackHelper: GPS not initialized or signal strength not high enough, aborting")
            return False

        if not self._ready_start_time:
            Logger.info("TrackHelper: waiting for RC warmup")
            self._ready_start_time = datetime.now()
            return False

        diff = datetime.now() - self._ready_start_time

        if diff.total_seconds() < self._wait_period:
            Logger.info("TrackHelper: waiting for RC warmup")
            return False

        if not self._tracks_loaded or not self.rc_config.trackConfig:
            return False

        return True

    def _check_track_detection(self):
        """
        If everything is ready, attempt to find a track in the app's local track db that is near
        where RC is now. Uses the track manager to find a track, if found adds it to RC Config's
        track db and fires the 'on_track_detected' event
        :return:
        """
        if self._is_ready():
            # Ok we are ready to go!

            Logger.info("TrackHelper: attempting to find track")

            geopoint = GeoPoint()
            geopoint.latitude = self._status['GPS']['lat']
            geopoint.longitude = self._status['GPS']['lon']

            track = self.track_manager.find_nearby_track(geopoint)

            if track:
                # Hooray!
                Logger.info("TrackHelper: found a track, adding it to RC config: {}".format(track.track_id))

                track_to_add = Track.fromTrackMap(track)

                # First, check if it's already in RC's config
                previously_added = [t for t in self.rc_config.trackDb.tracks if t.trackId == track_to_add.trackId]

                if len(previously_added) > 0:
                    Logger.info("TrackHelper: track found already in RC config, not adding")
                    return

                self.rc_config.trackDb.tracks.append(track_to_add)
                self.rc_config.trackDb.stale = True
                self.dispatch("on_track_detected")
            else:
                Logger.info("TrackHelper: no track found")
        else:
            Logger.info("TrackHelper: RC track detected or GPS not ready for track detection")



