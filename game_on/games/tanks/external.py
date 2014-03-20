#Allow easy access to some things
from constants import DIR

class ExternalTeam(object):
    def init_players(self, board_width, board_height, min_x, max_x, min_y, max_y):
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
        raise Exception('Teams must override the init_players method!')

    def run_tick(self, live_players, seen):
        """
        Work out what you want your team to do for the next tick
        @param: live_players A list of your players which are still alive
        @param: seen A list of {x:x, y:y} of seen enemy players
        """
        raise Exception('Teams must override the run_tick method!')
