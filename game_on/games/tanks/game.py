import math
import os

import cherrypy

from . import example_teams
from . import external
from . import projectile
from . import team
from . import utils
from game_on.games import base_game
from game_on.tools import jinja_tool


class TankGame(base_game.BaseGame):
    #Base properties
    name = 'GameOn.Tanks'
    description = 'A (fairly basic) 5-a-side tanks game'
    base_team = external.ExternalTeam
    example_team_file = 'example_team.py'

    cwd = os.path.dirname(os.path.abspath(__file__))
    static_folder = os.path.join(cwd, 'static')
    jinja2_env = jinja_tool.get_env(
        extra_paths=static_folder
    )

    #Tank specific properties
    width = 1000
    height = 800

    #################################################
    #       Setup
    #################################################

    @classmethod
    def get_example_teams(self):
        """
        Get any example teams which should be added to the team database
        @return: A list of dictionaries like:
            {
                'name': 'A nice name',
                'file': '/path/to/example/team.py',
                'is_public': False, (optional, default True)
            }
        """
        return example_teams.EXAMPLE_TEAMS

    #################################################
    #       Initialisation
    #################################################

    def initialise(self, team_classes):
        """
        Initialise this game. This includes ensure the teams are created and
        validated (e.g. stats are in correct ranges).
        Return an error message or None
        """
        #Initialise the teams
        self.team_1 = team.Team('team_1', team_classes[0], 'rgba(200, 50, 200, {alpha})')
        self.team_2 = team.Team('team_2', team_classes[1], 'rgba(128, 128, 255, {alpha})')

        #Initialise other storage
        self.projectiles = []

        #Initialise the players
        try:
            self.team_1.init_players(
                game=self,
                min_x=0.05 * self.width,
                max_x=0.25 * self.width,
                min_y=0.1  * self.height,
                max_y=0.9  * self.height,
                enemy_direction=0,
            )

            self.team_2.init_players(
                game=self,
                min_x=0.75 * self.width,
                max_x=0.95 * self.width,
                min_y=0.1  * self.height,
                max_y=0.9  * self.height,
                enemy_direction=math.pi,
            )
        except Exception, ex:
            raise
            return 'Error validating teams: %s' % str(ex)

    #################################################
    #       Serialisers
    #################################################

    def get_constant_state(self):
        """
        Return a dictionary of any game state which remains constant.

        Constant state for GameOn.Tanks is:
            {
                board: {
                    width: ,
                    height: ,
                },
                team_1: <team constant state>,
                team_2: <team constant state>,
                projectile: <projectile constant state>
            }
        """
        return {
            'board': {
                'width': self.width,
                'height': self.height,
            },
            'team_1': self.team_1.get_constant_state(),
            'team_2': self.team_2.get_constant_state(),
            'projectile': projectile.Projectile.get_constant_state()
        }

    def get_tick_state(self):
        """
        Return a dictionary of the current game state.
        This is compared to the previous game state to find changes which
        will be persisted

        Tick state for GameOn.Tanks is:
            {
                team_1: <team tick state>,
                team_2: <team tick state>,
                projectiles: [<projectile tick state>]
            }
        """
        return {
            'team_1': self.team_1.get_tick_state(),
            'team_2': self.team_2.get_tick_state(),
            'projectiles': [p.get_tick_state() for p in self.projectiles]
        }

    #################################################
    #       Setters
    #################################################

    def add_projectile(self, projectile):
        self.projectiles.append(projectile)

    def remove_projectile(self, projectile):
        self.projectiles.remove(projectile)

    #################################################
    #       Getters
    #################################################

    def is_complete(self):
        """
        Determine if this game is complete
        """
        return self.team_1.is_dead or self.team_2.is_dead

    def get_winners(self):
        """
        Determine who (if anyone) won this game
        """
        winners = []
        if not self.team_1.is_dead:
            winners.append('team_1')
        if not self.team_2.is_dead:
            winners.append('team_2')
        return winners

    #################################################
    #       Execution
    #################################################

    def run_tick(self):
        """
        Run one tick of this game
        This method must return a dictionary which is compared to the previous
        dictionary to find any changes to the game state
        """
        #Find out what everyone can see
        team_1_seen = self.team_1.get_seen(self.team_2.live_players)
        team_2_seen = self.team_2.get_seen(self.team_1.live_players)

        #Run the teams & players
        self.team_1.run_tick(team_1_seen)
        self.team_2.run_tick(team_2_seen)

        #Run the projectiles
        for projectile in self.projectiles:
            projectile.run_tick()

    def damage(self, x, y, r):
        """
        """
        def check_damage(team):
            for player in team.live_players:
                if player.distance_to(x, y) < r:
                    #Yes!
                    player.health -= utils.DAMAGE
        check_damage(self.team_1)
        check_damage(self.team_2)
