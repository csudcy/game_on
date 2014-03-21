import math

from. import player


class Team(object):
    #################################################
    #       Initialisation
    #################################################

    def __init__(self, id, external_team_class, effect_colour):
        """
        Create the team
        """
        #Create the team
        self.id = id
        self.external_team = external_team_class()
        self.effect_colour = effect_colour

    def init_players(
            self,
            board_width,
            board_height,
            min_x,
            max_x,
            min_y,
            max_y,
            enemy_direction,
        ):
        """
        Initialise & validate players
        """
        #Construct the class we can pass through to the external_team
        class TeamPlayer(player.Player):
            def __init__(self, **player_info):
                #Set the corrent min/max x/y
                self.STATS['x']['min'] = min_x
                self.STATS['x']['max'] = max_x
                self.STATS['y']['min'] = min_y
                self.STATS['y']['max'] = max_y
                super(TeamPlayer, self).__init__(
                    id=TeamPlayer.player_count,
                    board_width=board_width,
                    board_height=board_height,
                    **player_info
                )
                TeamPlayer.player_count += 1
        TeamPlayer.player_count = 0

        #Initialise players
        self.players = self.external_team.init_players(
            TeamPlayer,
            board_width,
            board_height,
            min_x,
            max_x,
            min_y,
            max_y,
            enemy_direction,
        )

        #Validate players
        for p in self.players:
            if not isinstance(p, TeamPlayer):
                raise Exception('Players must be an instance of TeamPlayer!')

    #################################################
    #       Serialisers
    #################################################

    def get_constant_state(self):
        """
        Return a dictionary of any team state which remains constant.

        Constant state for GameOn.Tanks.Team is:
            {
                name: ,
                player_count: ,
                max_health: ,
                effect_colour: , ('rgba(255, 0, 0, {alpha})')
                players: [<player constant state>, ...]
            },
        """
        return {
            'name': self.external_team.name,
            'player_count': len(self.players),
            'max_health': player.Player.get_max_health(),
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
        self.external_team.run_tick(self.live_players, seen)

        #Then run the players
        for live_player in self.live_players:
            live_player.run_tick()
