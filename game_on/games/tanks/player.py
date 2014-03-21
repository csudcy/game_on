import math

from . import utils


class Player(object):
    #################################################
    #       Initialisation
    #################################################

    def __init__(
                self,
                id,
                sight,
                health,
                blast_radius,
                board_width,
                board_height,

                x,
                y,

                speed,
                direction,
                turret_direction
            ):
        #Constant stats
        self.id = id
        self.sight = sight
        self.health = health
        self.blast_radius = blast_radius
        self.board_width = board_width
        self.board_height = board_height

        #Complex stats
        self.x = x
        self.y = y

        #Rate bound stats
        self.speed = utils.RateBoundVariable(
            current = 0,
            rate = 0.1,
            minimum = 0,
            maximum = speed,
        )
        self.direction = utils.RateBoundDirection(
            current = direction,
            rate = 0.1,
        )
        self.turret_direction = utils.RateBoundDirection(
            current = turret_direction,
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

        Constant state for GameOn.Tanks.Player is:
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

        Tick state for GameOn.Tanks.Player is:
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
            }
        """
        return {
            'x': self.x,
            'y': self.y,
            'direction': self.direction.current,
            'turret_direction': self.turret_direction.current,
            'is_dead': self.is_dead,
            'reload_frac': self.reload.current / self.reload.target,
            'target_x': self.target_x,
            'target_y': self.target_y,
            'target_r': self.target_r,
        }

    #################################################
    #       Setters
    #################################################

    def set_direction(val):
        self.direction.set_target(val)

    def set_turret_direction(val):
        self.turret_direction.set_target(val)

    def set_speed(val):
        self.speed.set_target(val)

    def set_target(x, y, r):
        self.target_x = max(min(x, self.board_width), 0)
        self.target_y = max(min(y, self.board_height), 0),
        self.target_r = r or 10

    def clear_target():
        self.target_x = None
        self.target_y = None
        self.target_r = None

    #################################################
    #       Getters
    #################################################

    @property
    def in_target():
        if not self.target_r:
            raise Exception('No target has been defined!')
        return self.distance_to(self.target_x, self.target_y) <= self.target_r

    @property
    def can_fire():
        #Check if this player can currently fire
        return self.reload.current == self.reload.target

    @property
    def is_dead(self):
        return self.health <= 0

    #################################################
    #       Calculators
    #################################################

    def angle_to(x, y):
        return math.atan2((y - self.y), (x - self.x))

    def calculate_firing_angle(distance):
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
        self.x = max(min(self.x + x_y[0], self.board_width), 0)
        self.y = max(min(self.y + x_y[1], self.board_height), 0)

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







"""
    ///// Actions
    fire: function(elevation) {
        //Fire a projectile
        var self=this;
        //Create the projectile
        //TODO: Incorporate tank direction & speed
        self.ai.board.add_projectile(new Projectile(
            self,
            self.position.x,
            self.position.y,
            0,
            self.turret_direction.current,
            elevation,
            10,
            self.stats.firepower
        ));
        //Make sure we can't fire again straight away
        self.reload.current = 0;
    },
"""
