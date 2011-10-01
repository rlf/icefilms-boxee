# A simple watch dog for the mc.Player
# TODO:
#  - add better granularity to the EVENT states.
import jobmanager
import time

class PlayerWatchDog(jobmanager.BoxeeJobManager):
    ''' Enables callback when a player doesn't start as it is expected to. '''
    def __init__(self, player, callback, token=None, timeout=10, interval=0.5):
        '''
            callback -- a function to be called with (success, token) once the
                        watchdog has some information.
            token    -- a token to be passed (verbatim) to the callback.
        '''
        self.callback = callback
        self.token = token
        jobmanager.BoxeeJobManager.__init__(self, interval, timeout*2)
        self.add_job(WatchDogJob(self, player, timeout, interval))
        self.start()

    def _callback(self, success):
        self.stop()
        self.callback(success, self.token)

class WatchDogJob(jobmanager.BoxeeJob):
    def __init__(self, manager, player, timeout, interval):
        jobmanager.BoxeeJob.__init__(self, 'WatchDogJob', interval)
        self.manager = manager
        self.player = player
        self.timeout = timeout
        self.start_state = player.GetLastPlayerEvent()
        self.start_time = time.time()
        self.log("STARTED")

    def process(self):
        t = time.time()
        diff = t - self.start_time
        state = self.player.GetLastPlayerEvent()
        if state != self.start_state:
            self.log("SUCCESS")
            self.manager._callback(True)
            return
        if diff > self.timeout:
            self.log("TIMEOUT")
            self.manager._callback(False)
