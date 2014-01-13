var AIBase = Class.extend({
    init: function(board, min_x, max_x, min_y, max_y, enemy_direction, effect_colour, effect_colour_alpha) {
        //Initialise this AI
        var self=this;
        self.players = [];
        self.board = board;
        self.effect_colour = effect_colour;
        self.effect_colour_alpha = effect_colour_alpha;

        var w=max_x-min_x, h=max_y-min_y;
        self.init_players(
            w,
            h,
            function(player) {
                if (player.position.x < 0 || player.position.y < 0 || player.position.x > w || player.position.y > h) {
                    throw new Error('Player placed out of bounds!');
                }
                player.ai = self;
                player.id = self.players.length;
                player.position.x += min_x;
                player.position.y += min_y
                self.players.push(player);
            }
        );
        if (self.players.length !== board.player_count) {
            throw new Error('Player count incorrect! Expected: '+board.player_count+', Actual: '+self.players.length);
        }
        self.update_live_players();
        //Make sure we point the right way
        self.players.forEach(function(player) {
            player.direction.current = enemy_direction;
            player.direction.target = enemy_direction;
            player.turret_direction.current = enemy_direction;
            player.turret_direction.target = enemy_direction;
        });
    },
    update_live_players: function() {
        var self=this;
        self.live_players = [];
        self.players.forEach(function(player) {
            if (!player.is_dead()) {
                self.live_players.push(player);
            }
        });
        return self;
    },
    draw: function(g) {
        //Draw all the players
        var self=this;
        for (var i=0; i<self.board.player_count; i++) {
            self.players[i].draw(g);
        }
        //Draw everything else?
        self.post_draw(g);
    },
    ///// Overridable functions \\\\\
    init_players: function(w, h, add_player) {
        //Required: 
        throw new Error('You must override init_players!');
    },
    post_draw: function(g) {
        //Optional: Called after all other drawing is complete
    },
    run: function(seen) {
        //Required: Work out what you want your team to do for the next tick
        //Seen is a list of {x:x, y:y} of enemy tanks
        throw new Error('You must override run!');
    }
});
