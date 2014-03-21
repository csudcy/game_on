import math
import random

from game_on.games.tanks import external


class Team(external.ExternalTeam):
    #Give the team a nice name
    name = 'Aggresive (Static : Random)'

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
        #We're not very nice, try to kill people!
        for player in live_players:
            if player.can_fire:
                #We're stupid, just fire at a random elevation in front
                player.fire(
                    #Make a random elevation somewhere between horizontal & vertical
                    random.uniform(1.0/8 * math.pi, 3.0/8 * math.pi)
                )
