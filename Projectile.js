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
    run: function() {
        var self=this;
        //Check we aren#t finished already
//if (Math.random() < 0.1) { console.log(self); }
//console.log('(' + self.x_current + ', ' + self.y_current + ', ' + self.z_current + '), (' + self.x_diff + ', ' + self.y_diff + ', ' + self.z_diff + ')');
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
    draw: function(g) {
        var self=this;
//if (Math.random() < 0.1) { console.log(self); }
//console.log(self);
        if (!self.is_complete()) {
            g.beginPath();
            g.moveTo(self.x_origin, self.y_origin);
            g.lineTo(self.x_current, self.y_current);
            g.strokeStyle = self.player.ai.effect_colour;
            g.stroke();
        } else {
            var r = self.power,
                opacity = 0.7;
            if (self.explosion_age < self.show_age) {
                r = r*(self.show_age-Math.abs(self.show_age - self.explosion_age))/self.show_age
            } else if (self.explosion_age > self.fade_age) {
                opacity = opacity * (self.max_age - self.explosion_age) / (self.max_age - self.fade_age);
            }
            g.beginPath();
            g.arc(self.x_current, self.y_current, r, 0, 2 * Math.PI, false);
            g.fillStyle = self.player.ai.effect_colour_alpha(opacity); //'rgba(255, 0, 0, ' + opacity + ')';
            g.fill();
        }
    }
});
