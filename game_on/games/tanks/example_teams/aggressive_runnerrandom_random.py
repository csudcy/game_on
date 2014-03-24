import math
import random

from game_on.games.tanks import external


class Team(external.ExternalTeam):
    #Give the team a nice name
    name = 'Aggresive (Runner-Random : Random)'

    def init_players(self, PlayerClass, board_width, board_height, min_x, max_x, min_y, max_y, enemy_direction):
        #Need these later...
        self.board_width = board_width
        self.board_height = board_height

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
            self.set_random_target(player)
            players.append(player)
        return players

    def set_random_target(self, player):
        player.set_target(
            random.randint(0, self.board_width),
            random.randint(0, self.board_height),
        )

    def run_tick(self, live_players, seen):
        for player in live_players:
            #We want to move around
            if player.in_target:
                self.set_random_target(player)

            #We're not very nice, try to kill people!
            if player.can_fire:
                #We're stupid, just fire at a random elevation in front
                player.fire(
                    #Make a random elevation somewhere between horizontal & vertical
                    random.uniform(1.0/32 * math.pi, 5.0/32 * math.pi)
                )
