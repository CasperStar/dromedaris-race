import logging, sys
from MotorController import MotorController

from Sensor import EdgeEventEnum

class TrackContainer:
    def __init__(self, number_of_tracks, score_start, score_max) -> None:
        logging.debug("TrackContainer: Initializing {:02s} Tracks".format(number_of_tracks))
        self.score_start = score_start
        self.score_max = score_max
        self.tracks = list()
        for i in range(0, number_of_tracks):
            self.tracks.append(ThrowingTrack(i, score_start, score_max))

    def get_track(self, index):
        return self.tracks[index]

    def try_get_winner(self):
        for track in self.track_container:
            if (track >= track. self.score_max):
                return True, track
        return False

    def print_score_overview(self):
        logging.info('-' * 20)
        logging.info("{: ^20}".format("SCORE OVERVIEW"))
        logging.info('-' * 20)
        for track in self.track_container:
            logging.info("Track ID: {:02} Score: {:02}".format(track.get_score(), track.get_track_id()))

    def reset_scores(self):
        logging.debug("TrackContainer: Reset all scores")
        for track in self.track_container:
            track.set_score(self.score_start)


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

    def reached_max_score(self) -> bool:
        if (self.score >= self.score_max):
            return True
        return False




