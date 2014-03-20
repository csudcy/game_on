
var AIMover = AIStatic.extend({
    init_players: function(w, h, add_player) {
        var self=this;
        self._super(w, h, add_player);
        self.players.forEach(function(player) {
            player.set_speed(
                999
            ).set_target(
                0.8*self.board.width,
                (player.id+1)/(self.board.player_count+1)*self.board.height,
                50
            );
        });
    }
});
AIMover.description = 'Dumb - Mover';

var AIRunner = AIStatic.extend({
    init_players: function(w, h, add_player) {
        var self=this;
        self._super(w, h, add_player);
        self.players.forEach(function(player) {
            player.set_speed(
                999
            ).set_target(
                0.9*self.board.width,
                player.position.y
            );
        });
    },
    run: function() {
        //Required:
        var self=this;
        self.live_players.forEach(function(player) {
            if (player.in_target()) {
                if (player.target.x > 0.5*self.board.width) {
                    player.target.x = 0.1*self.board.width;
                } else {
                    player.target.x = 0.9*self.board.width;
                }
            }
        });
    }
});
AIRunner.description = 'Dumb - Ordered Runner';

var AIRunnerRandom = AIStatic.extend({
    init_players: function(w, h, add_player) {
        var self=this;
        self._super(w, h, add_player);
        self.players.forEach(function(player) {
            player.set_speed(
                999
            ).set_target(
                Math.random()*self.board.width,
                Math.random()*self.board.height
            );
        });
    },
    run: function() {
        //Required:
        var self=this;
        self.live_players.forEach(function(player) {
            if (player.in_target()) {
                player.set_target(
                    Math.random()*self.board.width,
                    Math.random()*self.board.height
                );
            }
        });
    }
});
AIRunnerRandom.description = 'Dumb - Random Runner';

AIs.push(AIStatic, AIMover, AIRunner, AIRunnerRandom);
