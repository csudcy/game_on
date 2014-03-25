import math
import random

from team_not_found.games.tanks import external


class Team(external.ExternalTeam):
    #Give the team a nice name
    name = 'Aggresive (Static : Lookout)'

    #We don't want this team going public
    is_public = False

    def init_players(self, PlayerClass, board_width, board_height, min_x, max_x, min_y, max_y, enemy_direction):
        #Need these later...
        self.board_width = board_width
        self.board_height = board_height

        #Initialise the players
        players = []
        x = (min_x + max_x) / 2
        y_step = (max_y - min_y) / 4
        for i in xrange(5):
            player = PlayerClass(
                x=x,
                y=min_y + i * y_step,

                speed=0,
                sight=1,
                health=0,
                blast_radius=0,

                direction=enemy_direction,
                turret_direction=enemy_direction,
            )
            players.append(player)

        #TL
        players[0].set_target(
            0.25 * board_width,
            0.25 * board_height,
            10,
        )
        #TR
        players[1].set_target(
            0.75 * board_width,
            0.25 * board_height,
            10,
        )
        #Mid
        players[2].set_target(
            0.5 * board_width,
            0.5 * board_height,
            10,
        )
        #BR
        players[3].set_target(
            0.75 * board_width,
            0.75 * board_height,
            10,
        )
        #BL
        players[4].set_target(
            0.25 * board_width,
            0.75 * board_height,
            10,
        )

        #Done
        return players

    def run_tick(self, live_players, seen):
        fire_at = None
        if seen:
            fire_at = seen[0]

        for player in live_players:
            #We're not very nice, try to kill people!
            if fire_at:
                #Yes - make sure our turret is pointing the correct direction
                player.turret_direction.target = player.angle_to(fire_at.x, fire_at.y)
                #Also, make sure we're not moving
                player.set_speed(0)
                #Can we fire now?
                if player.can_fire and player.turret_direction.is_complete:
                    #TODO: Work out power to use
                    distance = player.distance_to(fire_at.x, fire_at.y)
                    angle = player.calculate_firing_angle(distance)
                    player.fire(angle)
