from game_on.games import base_game
from . import external
from . import team
from . import projectile


class TankGame(base_game.BaseGame):
    #Base properties
    name = 'GameOn.Tanks'
    description = 'A (fairly basic) 5-a-side tanks game'
    base_team = external.ExternalTeam
    example_team_file = 'example_team.py'

    #Tank specific properties
    width = 1000
    height = 800
    projectiles = []

    #################################################
    #       Initialisation
    #################################################

    def initialise_teams(self, team_classes):
        """
        Ensure the teams are created and are valid (e.g. stats are in correct ranges)
        Return an error message or None
        """
        #Initialise the teams
        self.team_1 = team.Team('team_1', team_classes[0], 'rgba(255, 255, 0, {alpha})')
        self.team_2 = team.Team('team_2', team_classes[1], 'rgba(128, 0, 128, {alpha})')

        #Initialise the players
        try:
            self.team_1.init_players(
                board_width = self.width,
                board_height = self.height,
                min_x = 0.05 * self.width,
                max_x = 0.25 * self.width,
                min_y = 0.1  * self.height,
                max_y = 0.9  * self.height,
            )

            self.team_2.init_players(
                board_width = self.width,
                board_height = self.height,
                min_x = 0.75 * self.width,
                max_x = 0.95 * self.width,
                min_y = 0.1  * self.height,
                max_y = 0.9  * self.height,
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
            'team_2': self.team_1.get_constant_state(),
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
            'team_2': self.team_1.get_tick_state(),
            'projectiles': [p.get_tick_state() for p in self.projectiles]
        }

    #################################################
    #       Setters
    #################################################

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
        raise Exception('Games must override the get_winners method!')

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
        team_1_seen = self.team_1.get_seen(self.team_2)
        team_2_seen = self.team_2.get_seen(self.team_1)

        #Run the teams & players
        self.team_1.run_tick(team_1_seen)
        self.team_2.run_tick(team_2_seen)

        #Run the projectiles
        for projectile in self.projectiles:
            projectile.run_tick()




"""
    damage: function(x, y, r) {
        var self=this;
        function check_damage(ai) {
            ai.live_players.forEach(function(player) {
                if (player.distance_to(x, y) < r) {
                    //Yes!
                    player.stats.health -= DAMAGE;
                    if (player.is_dead()) {
                        ai.update_live_players();
                    }
                }
            });
        }
        check_damage(self.ai_1);
        check_damage(self.ai_2);
    },

});
"""
