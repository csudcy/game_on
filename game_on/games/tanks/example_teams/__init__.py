import os

from . import dumb_static
from . import dumb_mover
from . import dumb_runner_ordered
from . import dumb_runner_random


cwd = os.path.dirname(os.path.abspath(__file__))

EXAMPLE_TEAMS = [
    {
        'name': dumb_static.Team.name,
        'path': os.path.join(cwd, 'dumb_static.py')
    },
    {
        'name': dumb_mover.Team.name,
        'path': os.path.join(cwd, 'dumb_mover.py')
    },
    {
        'name': dumb_runner_ordered.Team.name,
        'path': os.path.join(cwd, 'dumb_runner_ordered.py')
    },
    {
        'name': dumb_runner_random.Team.name,
        'path': os.path.join(cwd, 'dumb_runner_random.py')
    },
]
