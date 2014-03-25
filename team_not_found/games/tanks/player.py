import math

from . import utils
from . import projectile


class Player(object):
    #################################################
    #       Initialisation
    #################################################
    STATS = {
        #Absolute stats (just range checked)
        'x': {
            'min': 0, #Filled in by inheriting class
            'max': 0, #Filled in by inheriting class
        },
        'y': {
            'min': 0, #Filled in by inheriting class
            'max': 0, #Filled in by inheriting class
        },
        'direction': {
            'min': 0,
            'max': 2*math.pi,
        },
        'turret_direction': {
            'min': 0,
            'max': 2*math.pi,
        },

        #Variable stats (range checked & altered)
        'speed': {
            'min': 0,
            'max': 1,
            'add': 0.1,
            'mult': 10,
        },
        'sight': {
            'min': 0,
            'max': 1,
            'add': 0.2,
            'mult': 200,
        },
        'health': {
            'min': 0,
            'max': 1,
            'add': 0.2,
            'mult': 100,
        },
        'blast_radius': {
            'min': 0,
            'max': 1,
            'add': 0.1,
            'mult': 10000,
        },
    }

    def __init__(
                self,
                #Added by inheriting classes
                id,
                game,
                team,
                #Set by external_team
                **player_info
            ):
        """
        player_info = {
            'x': num (range: min_x-max_x),
            'y': num (range: min_y-max_y),

            'speed': num (range: 0-1),
            'sight': num (range: 0-1),
            'health': num (range: 0-1),
            'blast_radius': num (range: 0-1),

            'direction': num (range: 0-2*Pi),
            'turret_direction': num (range: 0-2*Pi),
        }
        """
        ########################################
        #       Validate stats
        ########################################

        #Check they haven't used too many points
        total_stats = player_info['speed']
        total_stats += player_info['sight']
        total_stats += player_info['health']
        total_stats += player_info['blast_radius']
        if total_stats > 1.0:
            raise Exception(
                'Player stats out of bounds: total @ {val} > 1.0'.format(
                    val = total_stats,
                )
            )

        #Check individual stats
        for stat in self.STATS:
            #Range check
            if player_info[stat] < self.STATS[stat]['min']:
                raise Exception(
                    'Player stat out of bounds: {stat} @ {val} < {min}'.format(
                        stat = stat,
                        val = player_info[stat],
                        min = self.STATS[stat]['min'],
                    )
                )
            if player_info[stat] > self.STATS[stat]['max']:
                raise Exception(
                    'Player stat out of bounds: {stat} @ {val} > {max}'.format(
                        stat = stat,
                        val = player_info[stat],
                        max = self.STATS[stat]['max'],
                    )
                )

            #Alter stat
            if 'add' in self.STATS[stat]:
                player_info[stat] = (player_info[stat] + self.STATS[stat]['add']) * self.STATS[stat]['mult']

        ########################################
        #       Save stats
        ########################################

        #Things we need to know
        self.id = id
        self.game = game
        self.team = team

        #Constant stats
        self.sight = player_info['sight']
        self.health = player_info['health']
        self.blast_radius = math.sqrt(player_info['blast_radius'])

        #Complex stats
        self.x = player_info['x']
        self.y = player_info['y']

        #Rate bound stats
        self.speed = utils.RateBoundVariable(
            current = 0,
            rate = 0.1,
            minimum = 0,
            maximum = player_info['speed'],
        )
        self.direction = utils.RateBoundDirection(
            current = player_info['direction'],
            rate = 0.1,
        )
        self.turret_direction = utils.RateBoundDirection(
            current = player_info['turret_direction'],
            rate = 0.2,
        )
        self.reload = utils.RateBoundVariable(
            current = 250,
            rate = 10,
        )

        #Settable stats
        self.target_x = None
        self.target_y = None
        self.target_r = None

    #################################################
    #       Serialisers
    #################################################

    def get_constant_state(self):
        """
        Return a dictionary of any player state which remains constant.

        Constant state for TeamNotFound.Tanks.Player is:
            {
                id: ,
                sight: ,
                blast_radius: ,
            }
        """
        return {
            'id': self.id,
            'sight': self.sight,
            'blast_radius': self.blast_radius,
        }

    def get_tick_state(self):
        """
        Return a dictionary of the current player state.

        Tick state for TeamNotFound.Tanks.Player is:
            {
                x: ,
                y: ,
                direction: ,
                turret_direction: ,
                is_dead: ,
                reload_frac: ,
                target_x: ,
                target_y: ,
                target_r: ,
                health: ,
            }
        """
        return {
            'x': self.x,
            'y': self.y,
            'direction': self.direction.current,
            'turret_direction': self.turret_direction.current,
            'is_dead': self.is_dead,
            'reload_frac': float(self.reload.current) / self.reload.target,
            'target_x': self.target_x,
            'target_y': self.target_y,
            'target_r': self.target_r,
            'health': self.health,
        }

    #################################################
    #       Setters
    #################################################

    def set_direction(self, val):
        self.direction.target = val

    def set_turret_direction(self, val):
        self.turret_direction.target = val

    def set_speed(self, val):
        self.speed.target = val

    def set_target(self, x, y, r=None):
        self.target_x = max(min(x, self.game.width), 0)
        self.target_y = max(min(y, self.game.height), 0)
        self.target_r = r or 10

    def clear_target(self):
        self.target_x = None
        self.target_y = None
        self.target_r = None

    #################################################
    #       Getters
    #################################################

    @property
    def in_target(self):
        if not self.target_r:
            raise Exception('No target has been defined!')
        return self.distance_to(self.target_x, self.target_y) <= self.target_r

    @property
    def can_fire(self):
        #Check if this player can currently fire
        return self.reload.current == self.reload.target

    @property
    def is_dead(self):
        return self.health <= 0

    @classmethod
    def get_max_health(cls):
        return (cls.STATS['health']['max'] + cls.STATS['health']['add']) * cls.STATS['health']['mult']

    #################################################
    #       Calculators
    #################################################

    def angle_to(self, x, y):
        return math.atan2((y - self.y), (x - self.x))

    def calculate_firing_angle(self, distance):
        #http://en.wikipedia.org/wiki/Trajectory_of_a_projectile#Angle_of_reach
        return math.asin(-utils.GRAVITY * distance / math.pow(10, 2)) / 2

    def distance_to(self, x, y):
        return math.sqrt(math.pow(self.x - x, 2) + math.pow(self.y - y, 2))

    def can_see(self, x, y):
        return self.distance_to(x, y) < self.sight

    #################################################
    #       Execution
    #################################################

    def run_tick(self):
        if self.is_dead:
            return
        #Update rate bound variables
        self.direction.update()
        self.turret_direction.update()
        self.speed.update()
        self.reload.update()
        #Make the turret move with the body
        self.turret_direction._target += self.direction._last_diff
        self.turret_direction._current += self.direction._last_diff

        #Update position
        x_y = utils.angle_speed_to_xy(self.direction.current, self.speed.current)
        self.x = max(min(self.x + x_y.x, self.game.width), 0)
        self.y = max(min(self.y + x_y.y, self.game.height), 0)

        #Check we're on target
        if self.target_r:
            #Check we're not turning too much & are not within our target
            if self.direction.is_complete:
                #We're heading the right direction, make sure we're moving
                self.set_speed(999)
                #Do we need to change direction?
                if not self.in_target:
                    #Work out where to point to next
                    self.set_direction(
                        self.angle_to(self.target_x, self.target_y)
                    )
            else:
                #We're not pointing the right direction yet, stop
                self.set_speed(0)

    def fire(self, elevation):
        """
        Fire a projectile
        """
        #Fire ze missiles
        projectile.Projectile(
            self,
            self.game,
            self.team,
            elevation,
        )

        #Make sure we can't fire again straight away
        self.reload._current = 0
