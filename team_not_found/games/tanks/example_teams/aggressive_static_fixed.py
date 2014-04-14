import math
import random

from team_not_found.games.tanks import external


class Team(external.ExternalTeam):
    #Give the team a nice name
    name = 'Aggressive (Static : Fixed)'

    #We don't want this team going public
    is_public = False

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
                speed=0,
                sight=0,
                health=0,
                blast_radius=100,
            )
            players.append(player)
        return players

    def run_tick(self, live_players, seen):
        for player in live_players:
            #We're not very nice, try to kill people!
            if player.can_fire:
                #We're stupid, just fire at a random elevation in front
                player.fire(
                    3.0/32 * math.pi,
                )
