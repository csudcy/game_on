from . import dumb_static
from . import dumb_mover
from . import dumb_runner_ordered
from . import dumb_runner_random

EXAMPLE_TEAMS = [
    dumb_static.Team,
    dumb_mover.Team,
    dumb_runner_ordered.Team,
    dumb_runner_random.Team,
]
