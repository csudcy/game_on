import os

from . import passive_static
from . import passive_mover
from . import passive_runner_ordered
from . import passive_runner_random

from . import aggresive_static_random
from . import aggresive_mover_random
#from . import aggresive_runner_ordered_random
#from . import aggresive_runner_random_random


cwd = os.path.dirname(os.path.abspath(__file__))

EXAMPLE_TEAMS = [
    {
        'name': passive_static.Team.name,
        'path': os.path.join(cwd, 'passive_static.py')
    },
    {
        'name': passive_mover.Team.name,
        'path': os.path.join(cwd, 'passive_mover.py')
    },
    {
        'name': passive_runner_ordered.Team.name,
        'path': os.path.join(cwd, 'passive_runner_ordered.py')
    },
    {
        'name': passive_runner_random.Team.name,
        'path': os.path.join(cwd, 'passive_runner_random.py')
    },

    {
        'name': aggresive_static_random.Team.name,
        'path': os.path.join(cwd, 'aggresive_static_random.py')
    },
    {
        'name': aggresive_mover_random.Team.name,
        'path': os.path.join(cwd, 'aggresive_mover_random.py')
    },
    #{
    #    'name': aggresive_runner_ordered_random.Team.name,
    #    'path': os.path.join(cwd, 'aggresive_runner_ordered_random.py')
    #},
    #{
    #    'name': aggresive_runner_random_random.Team.name,
    #    'path': os.path.join(cwd, 'aggresive_runner_random_random.py')
    #},
]
