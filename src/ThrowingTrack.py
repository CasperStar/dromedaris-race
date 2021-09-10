import logging, sys

from Sensor import EdgeEventEnum

class ThrowingTrack:
    def __init__(self, track_id, score_start, score_max) -> None:
        logging.debug("ThrowingTrack: Initializing Track ID:%s" %(track_id))
        self.track_id = track_id
        self.score_start = score_start
        self.score_max = score_max
        self.score = self.score_start

    def get_track_id(self) -> int:
        return self.track_id

    def add_score(self, value) -> int:
        self.score += value
        return self.score

    def set_score(self, value) -> int:
        self.score = value
        return self.score

    def get_score(self) -> int:
        return self.score




