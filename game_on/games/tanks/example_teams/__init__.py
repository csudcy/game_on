"""
Smart AI TODO:
  * Movement prediciton
  * Keep spotters moving
  * Danger close
  * ? Run away from enemies?
    * Turn back if they go out of sight though
"""
import os

from . import aggressive_static_random
from . import aggressive_mover_random
from . import aggressive_runner_ordered_random
from . import aggressive_runner_ordered_smart
from . import aggressive_runner_random_random

from . import passive_static
from . import passive_mover
from . import passive_runner_ordered
from . import passive_runner_random

from . import test_runner_ordered_random
from . import test_static_fixed


cwd = os.path.dirname(os.path.abspath(__file__))

EXAMPLE_TEAMS = [
    {
        'name': aggressive_static_random.Team.name,
        'path': os.path.join(cwd, 'aggressive_static_random.py'),
    },
    {
        'name': aggressive_mover_random.Team.name,
        'path': os.path.join(cwd, 'aggressive_mover_random.py'),
    },
    {
        'name': aggressive_runner_ordered_random.Team.name,
        'path': os.path.join(cwd, 'aggressive_runner_ordered_random.py'),
    },
    {
        'name': aggressive_runner_ordered_smart.Team.name,
        'path': os.path.join(cwd, 'aggressive_runner_ordered_smart.py'),
        'is_public': False,
    },
    {
        'name': aggressive_runner_random_random.Team.name,
        'path': os.path.join(cwd, 'aggressive_runner_random_random.py'),
    },

    {
        'name': passive_static.Team.name,
        'path': os.path.join(cwd, 'passive_static.py'),
    },
    {
        'name': passive_mover.Team.name,
        'path': os.path.join(cwd, 'passive_mover.py'),
    },
    {
        'name': passive_runner_ordered.Team.name,
        'path': os.path.join(cwd, 'passive_runner_ordered.py'),
    },
    {
        'name': passive_runner_random.Team.name,
        'path': os.path.join(cwd, 'passive_runner_random.py'),
    },

    {
        'name': test_runner_ordered_random.Team.name,
        'path': os.path.join(cwd, 'test_runner_ordered_random.py'),
        'is_public': False,
    },
    {
        'name': test_static_fixed.Team.name,
        'path': os.path.join(cwd, 'test_static_fixed.py'),
        'is_public': False,
    },
]
