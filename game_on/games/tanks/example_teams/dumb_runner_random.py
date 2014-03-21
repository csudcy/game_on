"""
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
"""
