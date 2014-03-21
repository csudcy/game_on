from game_on.games.tanks import external


class Team(external.ExternalTeam):
    #Give the team a nice name
    name = 'Example Team'

    def init_players(self, PlayerClass, board_width, board_height, min_x, max_x, min_y, max_y, enemy_direction):
        #Initialise the players
        players = []
        x = (min_x + max_x) / 2
        y_step = (max_y - min_y) / 4
        target_x = 0.8*board_width
        if x > 0.5 * board_width:
            target_x = 0.2 * board_width
        for i in xrange(5):
            player = PlayerClass(
                x=x,
                y=min_y + i * y_step,

                speed=0.25,
                sight=0.25,
                health=0.25,
                blast_radius=0.25,

                direction=enemy_direction,
                turret_direction=enemy_direction,
            )
            player.set_target(
                target_x,
                player.y,
                50
            )
            players.append(player)
        return players

    def run_tick(self, live_players, seen):
        #We're really dumb, nothing to do here!
        pass


"""
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
"""
