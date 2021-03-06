from team_not_found.games.tanks import external


class Team(external.ExternalTeam):
    #Give the team a nice name
    name = 'Passive (Static)'

    def init_players(self, PlayerClass, board_width, board_height, min_x, max_x, min_y, max_y, enemy_direction):
        #Initialise the players
        players = []
        x = (min_x + max_x) / 2
        y_step = (max_y - min_y) / 4
        for i in xrange(5):
            player = PlayerClass(
                x=x,
                y=min_y + i * y_step,
                direction=enemy_direction,
                turret_direction=enemy_direction,
                speed=25,
                sight=25,
                health=25,
                blast_radius=25,
            )
            players.append(player)
        return players

    def run_tick(self, live_players, seen):
        #We're really nice, nothing to do here!
        pass
