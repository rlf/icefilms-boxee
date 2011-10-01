import time
import unittest
from lib.playerwatchdog import *

class TestPlayerWatchDog(unittest.TestCase):

    def test_timeout(self):
        # Arrange
        player = self.create_player()
        token = [None]

        # Act
        PlayerWatchDog(player, callback, token, timeout=1, interval=0.1)

        # Assert
        self.assertEqual(token[0], None, "token : %s" % token)
        time.sleep(2)
        self.assertEqual(token[0], False, "token : %s" % token)
        
    def test_success(self):
        # Arrange
        player = self.create_player(0.2)
        token = [None]

        # Act
        PlayerWatchDog(player, callback, token, timeout=1, interval=0.1)

        # Assert
        self.assertEqual(token[0], None, "token : %s" % token)
        time.sleep(2)
        self.assertEqual(token[0], True, "token : %s" % token)
        
    def create_player(self, change_at = 100):
        return TestPlayer([(1,change_at), (2,0)])

def callback(success, token):
    print "CALLBACK %s" % success
    token[0] = success

class TestPlayer:
    def __init__(self, states=[(1,100)]):
        '''
            states -- list of tuples with (state, valid_until)
        '''
        self.states = states
        self.current_state = states.pop(0)
        self.start_time = time.time()

    def GetLastPlayerEvent(self):
        t = time.time()
        diff = t - self.start_time
        if self.current_state[1] < diff and len(self.states) > 0:
            print "PLAYER CHANGES STATE %s" % self.states
            self.current_state = self.states.pop(0)
        return self.current_state[0]

    def Play(self, item):
        self.start_time = time.time()
        
if __name__ == '__main__':
    unittest.main()