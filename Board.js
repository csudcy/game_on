var Board = Class.extend({
    init: function(container, player_count, update_timer, update_pause_state) {
        var self=this;
        self.container = container;
        self.player_count = player_count;
        self.update_timer = update_timer || function() {};
        self.update_pause_state = update_pause_state || function() {};
        self.width = container.width;
        self.height = container.height;
        self.set_paused(true);
        self.set_interval(50);
        self.run();
    },
    reset: function(ai_1_class, ai_2_class) {
        //Initialise this board
        var self=this;
        self.projectiles = [];
        self.time = 0;
        self.update_timer(self.time);
        self.ai_1 = new ai_1_class(
            self, //board
            0.05*self.width, //min_x
            0.25*self.width, //max_x
            0.1*self.height, //min_y
            0.9*self.height, //max_y
            0, //enemy_direction
            //[255, 255, 0] //effect_colour
            'rgb(255, 255, 0)', //effect_colour
            function(a) {
                return 'rgba(255, 255, 0, '+a+')';
            } //effect_colour_alpha
        );
        self.ai_2 = new ai_2_class(
            self, //board
            0.75*self.width, //min_x
            0.95*self.width, //max_x
            0.1*self.height, //min_y
            0.9*self.height, //max_y
            Math.PI, //enemy_direction
            //[128, 0, 128] //effect_colour
            'rgb(128, 0, 128)', //effect_colour
            function(a) {
                return 'rgba(128, 0, 128, '+a+')';
            } //effect_colour_alpha
        );
        self.set_paused(true);
        self.draw();
    },
    toggle_paused: function() {
        var self=this;
        self.set_paused(!self.paused);
    },
    set_paused: function(paused) {
        var self=this;
        self.paused = paused;
        self.update_pause_state(self.paused);
    },
    is_paused: function() {
        var self=this;
        return self.paused;
    },
    set_interval: function(interval) {
        var self=this;
        self.interval = interval;
    },
    get_interval: function() {
        var self=this;
        return self.interval;
    },
    get_time: function() {
        var self=this;
        return self.time;
    },
    add_projectile: function(projectile) {
        var self=this;
        self.projectiles.push(projectile);
    },
    remove_projectile: function(projectile) {
        var self=this;
        delete self.projectiles[self.projectiles.indexOf(projectile)];
    },
    damage: function(x, y, r) {
        var self=this;
        function check_damage(ai) {
            ai.live_players.forEach(function(player) {
                if (player.distance_to(x, y) < r) {
                    //Yes!
                    player.stats.health -= DAMAGE;
                    if (player.is_dead()) {
                        ai.update_live_players();
                    }
                }
            });
        }
        check_damage(self.ai_1);
        check_damage(self.ai_2);
    },
    run: function(single_step) {
        //Simulate all the things!
        var self=this;
        var next_interval = self.interval;
        if (single_step) {
            self.set_paused(true);
        }
        if (!self.is_paused() || single_step) {
            self.time++;
            self.update_timer(self.time);
            //Not pause, we should run the simulation
            function get_seen(ai_a, ai_b) {
                //Work out who ai_a.live_players can see of ai_b.live_players
                var seen = []
                for (var bi=0; bi<ai_b.live_players.length; bi++) {
                    var player_b = ai_b.live_players[bi];
                    for (var ai=0; ai<ai_a.live_players.length; ai++) {
                        var player_a = ai_a.live_players[ai];
                        //Can player_b be seen by player_a?
                        if (player_a.distance_to(player_b.position.x, player_b.position.y) < player_a.stats.sight) {
                            //Yes!
                            seen.push(player_b.position);
                            //No need to check if anyone else can see player_b
                            break;
                        }
                    }
                }
                return seen;
            }
            self.ai_1.run(get_seen(self.ai_1, self.ai_2));
            self.ai_2.run(get_seen(self.ai_2, self.ai_1));
            self.ai_1.live_players.forEach(function(p) {
                p.run();
            });
            self.ai_2.live_players.forEach(function(p) {
                p.run();
            });
            self.projectiles.forEach(function(projectile) {
                projectile.run();
            });
            self.draw();
        } else {
            //We are paused, no need to run very often
            next_interval = 500;
        }
        if (!single_step) {
            setTimeout(self.run.bind(self), next_interval);
        }
    },
    draw: function() {
        //
        var self=this;
        var g = self.container.getContext('2d');
        g.fillStyle = 'green';
        g.fillRect(0, 0, self.width, self.height);
        self.ai_1.draw(g);
        self.ai_2.draw(g);
        self.projectiles.forEach(function(projectile) {
            projectile.draw(g);
        });
    }
});
