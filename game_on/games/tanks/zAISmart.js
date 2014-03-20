var AISmart = AIBase.extend({
    init_players: function(w, h, add_player) {
        var self=this;
        add_player(
            new Player(
                self.board,
                0.5*w, // x,
                3/16*h, // y,
                0.2, // speed,
                0.8, // sight,
                0, // health,
                0 // firepower
            )
        );

        add_player(
            new Player(
                self.board,
                0.5*w, // x,
                2/8*h, // y,
                0.1, // speed,
                0, // sight,
                0.4, // health,
                0.5 // firepower
            )
        );

        add_player(
            new Player(
                self.board,
                0.5*w, // x,
                4/8*h, // y,
                0, // speed,
                0, // sight,
                0, // health,
                1 // firepower
            )
        );

        add_player(
            new Player(
                self.board,
                0.5*w, // x,
                6/8*h, // y,
                0.1, // speed,
                0, // sight,
                0.4, // health,
                0.5 // firepower
            )
        );

        add_player(
            new Player(
                self.board,
                0.5*w, // x,
                13/16*h, // y,
                0.2, // speed,
                0.8, // sight,
                0, // health,
                0 // firepower
            )
        );

        self.players.forEach(function(player) {
            player.set_speed(999);
            self.set_target(player);
        });

        self.target_track = [];
    },
    set_target: function(player) {
        var self=this;
        if (player.target === undefined) {
            player.set_target(
                0.9*self.board.width,
                player.position.y
            );
        } else if (player.target.x > 0.5*self.board.width) {
            player.target.x = 0.1*self.board.width;
        } else {
            player.target.x = 0.9*self.board.width;
        }
    },
    run: function(seen) {
        var self=this;
        if (seen.length > 0) {
            //Compare each seen enemy to our tracking data
            /*
            seen.forEach(function(enemy) {
                var min_distance, min_target_track;
                enemy.distance_to()
            });
            */
            self.fire_at = seen[0];
        } else {
            self.fire_at = undefined;
        }
        self.live_players.forEach(function(player) {
            if (player.in_target()) {
                self.set_target(player);
            }
            //Is there someone to aim at?
            if (self.fire_at) {
                //Yes - make sure our turret is pointing the correct direction
                player.set_turret_direction(player.angle_to(self.fire_at.x, self.fire_at.y));
                //Also, make sure we're not moving
                player.set_speed(0);
                //Can we fire now?
                if (player.can_fire() && player.turret_direction.is_complete()) {
                    //TODO: Work out power to use
                    var distance = player.distance_to(self.fire_at.x, self.fire_at.y);
                    var angle = player.calculate_firing_angle(distance);
                    player.fire(angle);
                }
            }
        });
    }
});
AISmart.description = 'Smart - Ordered';

var AISmartRandom = AISmart.extend({
    set_target: function(player) {
        var self=this;
        player.set_target(
            Math.random()*self.board.width,
            Math.random()*self.board.height
        );
    }
});
AISmartRandom.description = 'Smart - Random';

AIs.push(AISmart, AISmartRandom);
