from app import sessions

import time
from threading import Thread


class Cleaner(Thread):
    TIME_TO_SLEEP = 300
    KILL_TIME = 300

    def __init__(self):
        Thread.__init__(self)

    def run(self):
        time.sleep(self.TIME_TO_SLEEP)
        for session in sessions:
            if session.open and \
                    session.created_tm - time.time() > self.KILL_TIME:
                session.session.close()
                session.open = False
