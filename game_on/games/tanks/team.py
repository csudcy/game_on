import math

from. import player


class Team(object):
    #################################################
    #       Initialisation
    #################################################

    def __init__(self, id, team_class, effect_colour):
        """
        Create the team
        """
        #Create the team
        self.id = id
        self.team = team_class()
        self.effect_colour = effect_colour

    def init_players(self, board_width, board_height, min_x, max_x, min_y, max_y):
        """
        Initialise & validate players
        """
        #Initialise players
        player_infos = self.team.init_players(board_width, board_height, min_x, max_x, min_y, max_y)

        #Validate players
        stat_info = {
            #Absolute stats (just range checked)
            'x': {
                'min': min_x,
                'max': max_x,
            },
            'y': {
                'min': min_y,
                'max': max_y,
            },
            'direction': {
                'min': 0,
                'max': 2*math.pi,
            },
            'turret_direction': {
                'min': 0,
                'max': 2*math.pi,
            },

            #Variable stats (range checked & altered)
            'speed': {
                'min': 0,
                'max': 1,
                'add': 0.1,
                'mult': 10,
            },
            'sight': {
                'min': 0,
                'max': 1,
                'add': 0.2,
                'mult': 200,
            },
            'health': {
                'min': 0,
                'max': 1,
                'add': 0.2,
                'mult': 100,
            },
            'blast_radius': {
                'min': 0,
                'max': 1,
                'add': 0.1,
                'mult': 10000,
            },
        }

        self.max_health = (stat_info['health']['max'] + stat_info['health']['add']) * stat_info['health']['mult']

        self.players = []
        for player_info in player_infos:
            #Check they haven't used too many points
            total_stats = player_info['speed']
            total_stats += player_info['sight']
            total_stats += player_info['health']
            total_stats += player_info['blast_radius']
            if total_stats > 1.0:
                raise Exception(
                    'Player stats out of bounds: total @ {val} > 1.0'.format(
                        val = total_stats,
                    )
                )

            #Check individual stats
            for stat in stat_info:
                #Range check
                if player_info[stat] < stat_info[stat]['min']:
                    raise Exception(
                        'Player stat out of bounds: {stat} @ {val} < {min}'.format(
                            stat = stat,
                            val = player_info[stat],
                            min = stat_info[stat]['min'],
                        )
                    )
                if player_info[stat] > stat_info[stat]['max']:
                    raise Exception(
                        'Player stat out of bounds: {stat} @ {val} > {max}'.format(
                            stat = stat,
                            val = player_info[stat],
                            max = stat_info[stat]['max'],
                        )
                    )

                #Alter stat
                if 'add' in stat_info[stat]:
                    player_info[stat] = (player_info[stat] + stat_info[stat]['add']) * stat_info[stat]['mult']

            #Create player
            self.players.append(player.Player(
                id=len(self.players),
                board_width=board_width,
                board_height=board_height,
                **player_info
            ))

    #################################################
    #       Serialisers
    #################################################

    def get_constant_state(self):
        """
        Return a dictionary of any team state which remains constant.

        Constant state for GameOn.Tanks.Team is:
            {
                player_count: ,
                max_health: ,
                effect_colour: , ('rgba(255, 0, 0, {alpha})')
                players: [<player constant state>, ...]
            },
        """
        return {
            'player_count': len(self.players),
            'max_health': self.max_health,
            'effect_colour': self.effect_colour,
            'players': [p.get_constant_state() for p in self.players]
        }

    def get_tick_state(self):
        """
        Return a dictionary of the current team state.

        Tick state for GameOn.Tanks.Team is:
            {
                players: [<player tick state>, ...]
            }
        """
        return {
            'players': [p.get_tick_state() for p in self.players]
        }

    #################################################
    #       Setters
    #################################################

    #################################################
    #       Getters
    #################################################
    @property
    def live_players(self):
        return [p for p in self.players if not p.is_dead]

    @property
    def is_dead(self):
        """
        Check if all players are dead
        """
        for p in self.players:
            if not p.is_dead:
                return False
        #All players are dead :(
        return True

    #################################################
    #       Calculators
    #################################################

    def get_seen(self, enemy):
        my_players = self.live_players
        enemy_players = enemy.live_players
        seen = []
        #For each live enemy player
        for enemy_player in enemy_players:
            #Check if any one of our players can see them
            for my_player in my_players:
                #Can enemy_player be seen by my_player?
                if my_player.can_see(enemy_player.x, enemy_player.y):
                    #Yes!
                    seen.append((enemy_player.x, enemy_player.y))
                    #No need to check if anyone else can see player_b
                    break
        return seen

    #################################################
    #       Execution
    #################################################

    def run_tick(self, seen):
        #Pass through to the external team
        self.team.run_tick(self.live_players, seen)

        #Then run the players
        for live_player in self.live_players:
            live_player.run_tick()
