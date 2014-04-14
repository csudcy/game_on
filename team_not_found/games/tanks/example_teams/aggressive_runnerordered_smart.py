import math
import random

from team_not_found.games.tanks import external


class Team(external.ExternalTeam):
    #Give the team a nice name
    name = 'Aggresive (Runner-Ordered : Smart)'

    #We don't want this team going public
    is_public = False

    def init_players(self, PlayerClass, board_width, board_height, min_x, max_x, min_y, max_y, enemy_direction):
        #Need these later...
        self.board_width = board_width
        self.board_height = board_height

        #Initialise the players
        x = (min_x + max_x) / 2
        h = max_y - min_y

        players = [
            PlayerClass(
                x=x,
                y=min_y + 3.0/16*h,
                direction=enemy_direction,
                turret_direction=enemy_direction,
                speed=20,
                sight=80,
                health=0,
                blast_radius=0,
            ),
            PlayerClass(
                x=x,
                y=min_y + 4.0/16*h,
                direction=enemy_direction,
                turret_direction=enemy_direction,
                speed=10,
                sight=0,
                health=40,
                blast_radius=50,
            ),
            PlayerClass(
                x=x,
                y=min_y + 8.0/16*h,
                direction=enemy_direction,
                turret_direction=enemy_direction,
                speed=0,
                sight=0,
                health=0,
                blast_radius=1,
            ),
            PlayerClass(
                x=x,
                y=min_y + 12.0/16*h,
                direction=enemy_direction,
                turret_direction=enemy_direction,
                speed=10,
                sight=0,
                health=40,
                blast_radius=50,
            ),
            PlayerClass(
                x=x,
                y=min_y + 13.0/16*h,
                direction=enemy_direction,
                turret_direction=enemy_direction,
                speed=20,
                sight=80,
                health=0,
                blast_radius=0,
            ),
        ]

        #Set their targets
        target_x = 0.8*board_width
        if x > 0.5 * board_width:
            target_x = 0.2 * board_width
        for player in players:
            player.set_target(
                target_x,
                player.y
            )

        #Done
        return players

    def run_tick(self, live_players, seen):
        fire_at = None
        if seen:
            fire_at = seen[0]

        for player in live_players:
            #We want to move around
            if player.in_target:
                target_x = 0.8 * self.board_width
                if player.x > 0.5 * self.board_width:
                    target_x = 0.2 * self.board_width
                player.set_target(
                    target_x,
                    player.target_y
                )

            #We're not very nice, try to kill people!
            if fire_at:
                #Yes - make sure our turret is pointing the correct direction
                player.set_turret_direction(player.angle_to(fire_at.x, fire_at.y))
                #Also, make sure we're not moving
                player.set_speed(0)
                #Can we fire now?
                if player.can_fire and player.turret_direction.is_complete:
                    #TODO: Work out power to use
                    distance = player.distance_to(fire_at.x, fire_at.y)
                    angle = player.calculate_firing_angle(distance)
                    player.fire(angle)
