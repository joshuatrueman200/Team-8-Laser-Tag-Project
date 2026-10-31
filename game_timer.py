import math
import time


class GameTimer:
    def __init__(self, countdown_seconds=30, clock=None, game_duration_seconds=None):
        self.countdown_seconds = countdown_seconds
        self.game_duration_seconds = game_duration_seconds
        self.clock = clock or time.monotonic
        self.phase = 'idle'
        self.deadline = None

    def start(self):
        self.phase = 'countdown'
        self.deadline = self.clock() + self.countdown_seconds

    def reset(self):
        self.phase = 'idle'
        self.deadline = None

    def update(self):
        now = self.clock()
        if self.phase == 'countdown' and now >= self.deadline:
            self.phase = 'playing'
            self.deadline = (
                now + self.game_duration_seconds
                if self.game_duration_seconds is not None
                else None
            )
        elif self.phase == 'playing' and self.deadline is not None and now >= self.deadline:
            self.phase = 'finished'
            self.deadline = None

    def remaining(self):
        if self.deadline is None:
            return 0
        return max(0, math.ceil(self.deadline - self.clock()))

    def formatted(self):
        minutes, seconds = divmod(self.remaining(), 60)
        return f'{minutes:02d}:{seconds:02d}'
