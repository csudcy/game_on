"""
Smart AI TODO:
  * Movement prediciton
  * Keep spotters moving
  * Danger close
  * ? Run away from enemies?
    * Turn back if they go out of sight though
"""
import os

from . import aggressive_mover_random
from . import aggressive_runnerordered_random
from . import aggressive_runnerordered_siderandom
from . import aggressive_runnerordered_smart
from . import aggressive_runnerrandom_random
from . import aggressive_static_fixed
from . import aggressive_static_lookout
from . import aggressive_static_random
from . import passive_mover
from . import passive_runnerordered
from . import passive_runnerrandom
from . import passive_static


EXAMPLE_CLASSES = (
    aggressive_mover_random,
    aggressive_runnerordered_random,
    aggressive_runnerordered_siderandom,
    aggressive_runnerordered_smart,
    aggressive_runnerrandom_random,
    aggressive_static_fixed,
    aggressive_static_lookout,
    aggressive_static_random,
    passive_mover,
    passive_runnerordered,
    passive_runnerrandom,
    passive_static,
)

EXAMPLE_TEAMS = []
for example_class in EXAMPLE_CLASSES:
    filename = os.path.abspath(example_class.__file__)
    if os.path.splitext(filename)[1] == '.pyc':
        #We want the py file
        filename = filename[:-1]
    EXAMPLE_TEAMS.append({
        'name': example_class.Team.name,
        'path': filename,
        'is_public': getattr(example_class.Team, 'is_public', True),
    })
