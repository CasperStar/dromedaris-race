import logging, sys

from Sensor import EdgeEventEnum
from Motor import DCMotor, TurnDirection

class LaneContainer:
    def __init__(self, lane_mapping, motor_mapping) -> None:
        logging.debug(f"{type(self).__name__}: Initializing with {len(lane_mapping)} lanes")

        self.lanes = lane_mapping

        # for it in lane_objects:
        #     self._lanes.append(lane_objects)
        # for i in range(0, number_of_tracks):
        #     self.lanes.append(Lane(i, score_start, score_max,  motor_mapping[i]))

    def get_track(self, index):
        return self.lanes[index]

    def try_get_winner(self):
        for track in self.lanes:
            if (track >= track. self.score_max):
                return True, track
        return False

    def print_score_overview(self):
        logging.info('-' * 20)
        logging.info("{: ^20}".format("SCORE OVERVIEW"))
        logging.info('-' * 20)
        for track in self.lanes:
            logging.info("Track ID: {:02} Score: {:02}".format(track.get_track_id(), track.get_score()))

    def reset_scores(self):
        logging.debug("TrackContainer: Reset all scores")
        for track in self.lanes:
            track.set_score(self.score_start)

    def pause_motors(self):
        for track in self.lanes:
            track.pause_motor()

class Lane:
    def __init__(self, lane_id: int, score_start: int, score_max: int, motor) -> None:
        logging.debug(f"{type(self).__name__}: Initializing Lane ID:{lane_id}")
        self.lane_id = lane_id
        self.score_start = score_start
        self.score_max = score_max
        self.score = self.score_start
        self.motor = motor #TODO: Rework motor implemenation

    def get_track_id(self) -> int:
        return self.lane_id

    def add_score(self, value: int) -> int:
        self.score += value
        #self.motor.run_async(TurnDirection.CLOCKWISE, 100, 2000) #TODO: Rework motor implemenation
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

    def pause_motor(self):
        #self.motor.pause_async_thread() #TODO: Rework motor implemenation
        pass

