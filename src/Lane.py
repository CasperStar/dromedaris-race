import logging, sys
from MotorControl import MotorActionEnum

from Sensor import EdgeEventEnum
from MotorControl import Motor

class LaneContainer:
    def __init__(self, lane_mapping) -> None:
        logging.debug(f"{type(self).__name__}: Initializing with {len(lane_mapping)} lanes")
        self.lanes = lane_mapping

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

    def reset_scores_and_motors(self):
        logging.debug("TrackContainer: Reset all scores and motors")
        for lane in self.lanes:
            lane.reset_score_and_motor()

    def all_motor_events_processed(self) -> bool:
        for lane in self.lanes:
            if (not lane.all_motor_events_processed()):
                return False

        return True

    def pause_motors(self):
        for lane in self.lanes:
            lane.pause_motor()

class Lane:
    def __init__(self, lane_id: int, score_start: int, score_max: int, motor: Motor, motor_speed: int, motor_duration_ms: int) -> None:
        logging.debug(f"{type(self).__name__}: Initializing Lane ID:{lane_id}")
        self.lane_id = lane_id
        self.score_start = score_start
        self.score_max = score_max
        self.score = self.score_start
        self.motor = motor
        self.motor_speed_pct = motor_speed
        self.motor_run_duration_ms = motor_duration_ms

    def get_track_id(self) -> int:
        return self.lane_id

    def add_score(self, value: int) -> int:
        self.score += value
        self.motor.run_for(MotorActionEnum.TURN_CLOCKWISE, self.motor_speed_pct, self.motor_run_duration_ms)
        return self.score

    def reset_score_and_motor(self):
        accumulated_duration = self.motor_run_duration_ms * self.score
        self.set_score(0)

        if (accumulated_duration > 0):
            self.motor.run_for(MotorActionEnum.TURN_ANTI_CLOCKWISE, self.motor_speed_pct, accumulated_duration)

    def all_motor_events_processed(self) -> bool:
        return self.motor.all_events_processed()

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
        self.motor.pause_thread()
        pass

