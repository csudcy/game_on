"""
Example implementation of a player for GameOn.Tanks!

Useful methods available on Players:
    If you want to manually control your player:
        set_direction(radians) - Set the direction you want the player to face.
        set_turret_direction(radians) - Set the direction you want the players
            turret to face.
        set_speed(val) - Set the speed you want the player to move
    If you want your player to move to a spot automatically:
        set_target(x, y, r) - Set a target for the player & a radius to stay
            in. The player will move constantly but will try to keep within
            r distance from (x,y).
    Either way:
        fire(elevation) - Fire a projectile!

TODO: Write about tanks, turrets, speed, rate bound variables, blast_radius, sight, health, speed

Directions:
    North 3Pi/2
    East  0
    South Pi/2
    West  Pi
"""

from game_on.games.tanks import external


class Team(external.ExternalTeam):
    #Give the team a nice name
    name = 'Dumb - Static'

    def init_players(self, board_width, board_height, min_x, max_x, min_y, max_y, enemy_direction):
        """
        Initalise your players
        @param board_width: The width of the board
        @param board_height: The height of the board
        @param min_x: The minimum x position you may place a player at
        @param max_x: The maximum x position you may place a player at
        @param min_y: The minimum y position you may place a player at
        @param max_y: The maximum y position you may place a player at
        @return: List of 5 Player dicts of {
                'x': num (range: min_x-max_x),
                'y': num (range: min_y-max_y),
                'speed': num (range: 0-1),
                'sight': num (range: 0-1),
                'health': num (range: 0-1),
                'blast_radius': num (range: 0-1),
                'direction': num (range: 0-2*Pi),
                'turret_direction': num (range: 0-2*Pi),
            }
            Note: The sum of speed, sight, health & blast_radius must be <= 1
        """
        #Initialise the players
        players = []
        x = (min_x + max_x) / 2
        y_step = (max_y - min_y) / 4
        for i in xrange(5):
            players.append({
                'x': x,
                'y': min_y + i * y_step,
                'speed': 0.25,
                'sight': 0.25,
                'health': 0.25,
                'blast_radius': 0.25,
                'direction': enemy_direction,
                'turret_direction': enemy_direction,
            })
        return players

    def run_tick(self, live_players, seen):
        """
        Work out what you want your team to do for the next tick
        @param: live_players A list of your players which are still alive
        @param: seen A list of {x:x, y:y} of seen enemy players
        """
        #We're really dumb, nothing to do here!
        pass
