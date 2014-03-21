from . import utils

class Projectile(object):
    show_age = 5
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
            x,
            y,
            direction,
            elevation,
            blast_radius
        ):
        #Break speed & angles into vector components
        horz_vert = utils.angle_speed_to_xy(elevation, self.speed)
        x_y = utils.angle_speed_to_xy(direction, horz_vert.x)

        #Save all the things
        self.player = player
        self.game = game
        self.team = team
        self.origin_x = x
        self.origin_y = y
        self.origin_z = 0
        self.current_x = x
        self.current_y = y
        self.current_z = 0
        self.diff_x = x_y.x
        self.diff_y = x_y.y
        self.diff_z = horz_vert.y
        self.blast_radius = blast_radius
        self.explosion_age = 0

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
                show_age: 5,
                fade_age: 15,
                max_age: 20,
            }
        """
        return {
            'show_age': Projectile.show_age,
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
            if self.explosion_age < self.show_age:
                #We are still exploding
                damage_radius = float(self.blast_radius)
                damage_radius *= float(self.explosion_age) / float(self.show_age)
                print damage_radius
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
