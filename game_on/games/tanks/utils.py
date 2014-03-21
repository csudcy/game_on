import math


GRAVITY = -0.1
DAMAGE = 10


def angle_speed_to_xy(angle, speed):
    return (
        speed * math.cos(angle),
        speed * math.sin(angle)
    )


class RateBoundVariable(object):
    def __init__(self, current, rate, minimum=None, maximum=None):
        self._current = current
        self._target = current
        self._rate = rate
        self._minimum = minimum
        self._maximum = maximum

    @property
    def current(self):
        return self._current

    @property
    def target(self):
        return self._target
    @target.setter
    def target(self, value):
        value = max(value, self._minimum)
        value = min(value, self._maximum)
        self._target = value

    @property
    def is_complete(self):
        """
        Is this current value at (or close to) the target value?
        """
        #return self._target == self._current
        return abs(self._target - self._current) < 0.1;

    def check_target_bounds(self, val):
        """
        Check this value is within the bounds of this variable
        """
        return val

    def update(self):
        """
        Update current obeying rate and target
        """
        self._last_diff = 0
        if not self.is_complete:
            diff = self.check_target_bounds(self._target - self._current)
            if (diff < 0):
                diff = max(diff, -self._rate)
            else:
                diff = min(diff, self._rate)
            self._current = self.check_target_bounds(self._current + diff)
            self._last_diff = diff


class RateBoundDirection(RateBoundVariable):
    @property
    def target(self):
        return self._target
    @target.setter
    def target(self, value):
        self._target = self.check_target_bounds(value)

    def check_target_bounds(self, val):
        while (val < -math.pi):
            val += 2*math.pi
        while (val >= math.pi):
            val -= 2*math.pi
        return val
