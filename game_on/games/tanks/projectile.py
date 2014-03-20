class Projectile(object):
    #################################################
    #       Initialisation
    #################################################

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
            'show_age': 5,
            'fade_age': 15,
            'max_age': 20,
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
            'team': self.team,
            'player': self.player,
            'explosion_age': self.explosion_age,
        }

    #################################################
    #       Setters
    #################################################

    #################################################
    #       Getters
    #################################################

    #################################################
    #       Execution
    #################################################

    def run_tick(self):
        raise Exception('Implement projectile.run_tick!')
        """
        run: function() {
            var self=this;
            //Check we aren#t finished already
            if (!self.is_complete()) {
                self.x_current += self.x_diff;
                self.y_current += self.y_diff;
                self.z_current += self.z_diff;
                self.z_diff += GRAVITY;
            } else {
                //Is it can be assplosion tiem nao?
                if (self.explosion_age < self.show_age) {
                    self.player.ai.board.damage(
                        self.x_current,
                        self.y_current,
                        self.power*(self.show_age-Math.abs(self.show_age - self.explosion_age))/self.show_age
                    );
                }
                self.explosion_age++;
                if (self.explosion_age > self.max_age) {
                    //Stop now
                    self.player.ai.board.remove_projectile(self);
                }
            }
        },
        """






"""
var Projectile = Class.extend({
    init: function(player, x, y, z, direction, elevation, speed, power) {
        var self=this;
        //Break speed & angles into vector components
        var horz_vert = angle_speed_to_xy(elevation, speed);
        var x_y = angle_speed_to_xy(direction, horz_vert.x);
        //Save all the things
        self.player = player;
        self.x_origin = x;
        self.y_origin = y;
        self.z_origin = z;
        self.x_current = x;
        self.y_current = y;
        self.z_current = z;
        self.x_diff = x_y.x;
        self.y_diff = x_y.y;
        self.z_diff = horz_vert.y;
        self.power = power;
        self.explosion_age = 0;
        self.show_age = 5;
        self.fade_age = 15;
        self.max_age = 20;
    },
    is_complete: function() {
        var self=this;
        return (self.z_current <= 0 && self.z_diff <= 0);
    },
});
"""
