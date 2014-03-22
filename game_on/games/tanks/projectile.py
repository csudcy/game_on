import random

from . import utils

class Projectile(object):
    expand_age = 5
    fade_age = 15
    max_age = 20
    speed = 10

    #################################################
    #       Initialisation
    #################################################

    def __init__(
            self,
            player,
            game,
            team,
            elevation
        ):
        #Break speed & angles into vector components
        horz_vert = utils.angle_speed_to_xy(
            elevation,
            self.speed,
        )
        proj_x_y = utils.angle_speed_to_xy(
            player.turret_direction.current,
            horz_vert.x,
        )

        #Incorporate tank speed & direction
        tank_x_y = utils.angle_speed_to_xy(
            player.direction.current,
            player.speed.current,
        )

        #Save all the things
        self.player = player
        self.game = game
        self.team = team
        self.origin_x = player.x
        self.origin_y = player.y
        self.origin_z = 0
        self.current_x = player.x
        self.current_y = player.y
        self.current_z = 0
        self.diff_x = proj_x_y.x + tank_x_y.x
        self.diff_y = proj_x_y.y + tank_x_y.y
        self.diff_z = horz_vert.y
        self.blast_radius = player.blast_radius
        self.explosion_age = 0

        #Add random variation to shots based on current speed
        variation = (self.player.speed.current + 10) / 100.0
        self.diff_x += random.uniform(-0.5*variation, 0.5*variation)
        self.diff_y += random.uniform(-0.5*variation, 0.5*variation)
        self.diff_z += random.uniform(-0.2*variation, 0.2*variation)

        #Add myself to the game
        self.game.add_projectile(self)

    #################################################
    #       Serialisers
    #################################################

    @classmethod
    def get_constant_state(cls):
        """
        Return a dictionary of any projectile state which remains constant.

        Constant state for GameOn.Tanks.Projectile is:
            {
                expand_age: 5,
                fade_age: 15,
                max_age: 20,
            }
        """
        return {
            'expand_age': Projectile.expand_age,
            'fade_age': Projectile.fade_age,
            'max_age': Projectile.max_age,
        }

    def get_tick_state(self):
        """
        Return a dictionary of the current projectile state.

        Tick state for GameOn.Tanks.Projectile is:
            {
                is_at_target: ,
                origin_x: ,
                origin_y: ,
                current_x: ,
                current_y: ,
                team: , (team_1, team_2)
                player: , (0-4)
                explosion_age: ,
            }
        """
        return {
            'is_at_target': self.is_at_target,
            'origin_x': self.origin_x,
            'origin_y': self.origin_y,
            'current_x': self.current_x,
            'current_y': self.current_y,
            'team_id': self.team.id,
            'player_id': self.player.id,
            'explosion_age': self.explosion_age,
        }

    #################################################
    #       Setters
    #################################################

    #################################################
    #       Getters
    #################################################

    @property
    def is_at_target(self):
        return self.current_z <= 0 and self.diff_z <= 0

    #################################################
    #       Execution
    #################################################

    def run_tick(self):
        #Check if we're finished yet
        if not self.is_at_target:
            self.current_x += self.diff_x
            self.current_y += self.diff_y
            self.current_z += self.diff_z
            self.diff_z += utils.GRAVITY
        else:
            #Is it can be assplosion tiem nao?
            if self.explosion_age < self.expand_age:
                #We are still exploding
                damage_radius = float(self.blast_radius)
                damage_radius *= float(self.explosion_age) / float(self.expand_age)
                self.game.damage(
                    self.current_x,
                    self.current_y,
                    damage_radius,
                )
            elif self.explosion_age > self.max_age:
                #Remove myself from the game
                self.game.remove_projectile(self)

            #Advance the doom token
            self.explosion_age += 1
