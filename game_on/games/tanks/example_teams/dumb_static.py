from game_on.games.tanks import external


class Team(external.ExternalTeam):
    #Give the team a nice name
    name = 'Dumb Static'

    def init_players(self, PlayerClass, board_width, board_height, min_x, max_x, min_y, max_y, enemy_direction):
        #Initialise the players
        players = []
        x = (min_x + max_x) / 2
        y_step = (max_y - min_y) / 4
        for i in xrange(5):
            players.append(PlayerClass(
                x=x,
                y=min_y + i * y_step,

                speed=0.25,
                sight=0.25,
                health=0.25,
                blast_radius=0.25,

                direction=enemy_direction,
                turret_direction=enemy_direction,
            ))
        return players

    def run_tick(self, live_players, seen):
        #We're really dumb, nothing to do here!
        pass
