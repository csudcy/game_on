var Player = Class.extend({
    init: function(ai, x, y, speed, sight, health, firepower) {
        var self=this;

        //Check params are valid
        if (speed < 0 || sight < 0 || health < 0 || firepower < 0) {
            throw new Error('Stats must be positive!');
        }
        if (speed + sight + health + firepower !== 1.0) {
            throw new Error('Used too many stats points!');
        }

        function calculate(base, type) {
            return (base + STAT_MIN[type]) * STAT_MULT[type];
        }

        //Save everything
        self.ai = ai;
        self.position = {
            x: x,
            y: y
        };
        self.direction = new RateBoundDirection(
            0,
            0.1
        );
        self.turret_direction = new RateBoundDirection(
            0,
            0.2
        );
        self.speed = new RateBoundVariable(
            0,
            calculate(0, 'ACCELERATION'),
            0,
            calculate(speed, 'SPEED')
        );
        self.reload = new RateBoundVariable(
            250,
            calculate(0, 'RELOAD')
        );
        self.stats = {
            sight: calculate(sight, 'SIGHT'),
            health: calculate(health, 'HEALTH'),
            max_health: calculate(1.0, 'HEALTH'),
            firepower: Math.sqrt(calculate(firepower, 'FIREPOWER'))
        };
    },
    ///// Setters \\\\\
    set_direction: function(val) {
        this.direction.set_target(val);
        return this;
    },
    set_turret_direction: function(val) {
        this.turret_direction.set_target(val);
        return this;
    },
    set_speed: function(val) {
        this.speed.set_target(val);
        return this;
    },
    set_target: function(x, y, r) {
        if (r === undefined) {
            r = 10;
        }
        this.target = {
            x: Math.max(Math.min(x, this.ai.board.width), 0),
            y: Math.max(Math.min(y, this.ai.board.height), 0),
            r: r
        }
        return this;
    },
    ///// Getters \\\\\
    clear_target: function() {
        this.target = undefined;
        return this;
    },
    in_target: function() {
        if (this.target === undefined) {
            throw new Error('No target has been defined!');
        }
        return this.distance_to(this.target.x, this.target.y) <= this.target.r;
    },
    can_fire: function() {
        //Check if this player can currently fire
        return this.reload.current == this.reload.target;
    },
    is_dead: function() {
        return this.stats.health <= 0;
    },
    ///// Calculators \\\\\
    distance_to: function(x, y) {
        var self=this;
        return Math.sqrt(Math.pow(self.position.x - x, 2) + Math.pow(self.position.y - y, 2));
    },
    angle_to: function(x, y) {
        var self=this;
        return Math.atan2((y - self.position.y), (x - self.position.x));
    },
    calculate_firing_angle: function(distance) {
        //http://en.wikipedia.org/wiki/Trajectory_of_a_projectile#Angle_of_reach
        return Math.asin(-GRAVITY * distance / Math.pow(10, 2)) / 2;
    },
    ///// Actions \\\\\
    fire: function(angle) {
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
            angle,
            10,
            self.stats.firepower
        ));
        //Make sure we can't fire again straight away
        self.reload.current = 0;
    },
    ///// Simulation/UI \\\\\
    run: function() {
        var self=this;
        if (self.is_dead()) {
            return;
        }
        //Update rate bound variables
        self.direction.update();
        //Make the turret move with the body
        self.turret_direction.target += self.direction.last_diff;
        self.turret_direction.current += self.direction.last_diff;
        self.turret_direction.update();
        self.speed.update();
        self.reload.update();
        //Update position
        var x_y = angle_speed_to_xy(self.direction.current, self.speed.current);
        self.position.x = Math.max(Math.min(self.position.x + x_y.x, self.ai.board.width), 0);
        self.position.y = Math.max(Math.min(self.position.y + x_y.y, self.ai.board.height), 0);
        //Check we're on target
        if (self.target) {
            //Check we're not turning too much & are not within our target
            if (self.direction.is_complete()) {
                //We're heading the right direction, make sure we're moving
                self.set_speed(999);
                //Do we need to change direction?
                if (!self.in_target()) {
                    //Work out where to point to next
                    self.set_direction(self.angle_to(self.target.x, self.target.y));
                }
            } else {
                //WE're not pointing the right direction yet, stop
                self.set_speed(0);
            }
        }
    },
    draw: function(g) {
        //Draw this player
        var self=this;
        //Move to where we are
        g.save();
            g.translate(self.position.x, self.position.y);
            //Body
            g.save();
            g.rotate(self.direction.current);
            g.beginPath();
            g.moveTo(-10, -15);
            g.lineTo( 25,   0);
            g.lineTo(-10,  15);
            g.closePath();
            g.strokeStyle = 'black';
            g.stroke();
            g.restore();
            //Turret
            g.save();
            g.rotate(self.turret_direction.current);
            g.beginPath();
            g.moveTo(- 5, -5);
            g.lineTo( 15,  0);
            g.lineTo(- 5,  5);
            g.closePath();
            if (self.is_dead()) {
                g.fillStyle = 'grey';
            } else {
                g.fillStyle = 'rgba(255, 0, 0, ' + (self.reload.current / self.reload.target) + ')';
            }
            g.fill();
            g.strokeStyle = 'red';
            g.stroke();
            g.restore();
            if (!self.is_dead()) {
                //Sight
                g.beginPath();
                g.arc(0, 0, self.stats.sight, 0, 2 * Math.PI, false);
                g.strokeStyle = 'white';
                g.stroke();
                g.closePath();
                //Health
                g.save();
                g.fillStyle = 'green';
                g.fillRect(-35, 25, 70, 10);
                g.fillStyle = 'white';
                g.fillRect(-35, 25, (self.stats.health / self.stats.max_health) * 70, 10);
                g.strokeStyle = 'black';
                g.strokeRect(-35, 25, 70, 10);
                g.restore();
            }
            //Central point
            g.fillStyle = 'white';
            g.fillRect(-1, -1, 2, 2);
            //Id
            g.fillStyle = self.ai.effect_colour;
            g.fillText(self.id, 0, -20);
        g.restore();
        //Draw target
        if (self.target && !self.is_dead()) {
            g.beginPath();
            g.arc(self.target.x, self.target.y, self.target.r, 0, 2 * Math.PI, false);
            g.strokeStyle = self.ai.effect_colour;
            g.stroke();
            g.closePath();
        }
    }
});
