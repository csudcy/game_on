
class BaseGame(object):
    """
    Final output:
        {
            'status': 'State of the game',
            (e.g.
                "Error - team init failed",
                "Finished (Too many ticks)",
                "Finished"
            )
            'winners': ['team_1', 'team_2'],
            (multiple winners => draw)
            'ticks': [
                {
                    'team_1': {
                        'name': 'Dumb Team',
                        'stats': {
                            'health': 100,
                            'range': 50
                        },
                        'position': {
                            'x': 10,
                            'y': 20
                        }
                    },
                    'team_2': ...,
                    'projectiles': [
                        {
                            'x': 15,
                            'y': 15,
                            ...
                        }
                        ...
                    ]
                },
                ...
            ]
        }
    """
    #A nice name for this game
    name = None

    #A brief description of this game
    description = None

    #Maximum number of ticks a game can last
    max_ticks = 10000

    #The expected number of teams
    team_count = 2

    #The class which all teams must extend from
    base_team = None

    #Example team file which users download to show them how to make a team
    example_team_file = None

    def __init__(self, team_classes):
        if self.name is None:
            raise Exception(
                'You must define a name attribute on the game "{name}"!'.format(
                    name = self.name,
                ))
        if self.example_team_file is None:
            raise Exception(
                'You must define an example_team_file attribute on the game "{name}"!'.format(
                    name = self.name,
                ))
        if self.base_team is None:
            raise Exception(
                'You must define a base_team attribute on the game "{name}"!'.format(
                    name = self.name,
                ))
        if len(team_classes) != self.team_count:
            raise Exception(
                'The game "{name}" requires exactly {team_count} teams!'.format(
                    name = self.name,
                    team_count = self.team_count,
                ))
        for team_class in team_classes:
            if not issubclass(team_class, self.base_team):
                raise Exception(
                    'All teams of "{name}" must extend "{base_team}"!'.format(
                        name = self.name,
                        base_team = self.base_team,
                    ))

        #Save this for later
        self.team_classes = team_classes

    def run(self):
        """
        Run this game until it ends
        """
        #Initialise the return structure
        match = {
            'status': None,
            'winners': None,
            'constant_state': None,
            'ticks': []
        }

        #Initialise the teams
        error = self.initialise_teams(self.team_classes)
        if error:
            match['status'] = 'Error - team init failed: %s' % error
        else:
            #Populate the constant state info
            match['constant_state'] = self.get_constant_state()

            #Tick until the game ends
            previous_state = self.get_tick_state()
            match['ticks'].append(previous_state)
            while (True):
                #Check if we have run too many ticks
                if len(match['ticks']) > self.max_ticks:
                    match['status'] = 'Finished (Too many ticks)'
                    break

                from pprint import pprint as pp
                #pp(match)

                if len(match['ticks']) % 100 == 0:
                    print len(match['ticks'])

                #Run a tick
                self.run_tick()

                #Get the changed game state
                current_state = self.get_tick_state()
                #changed_state = self.get_changed_state(previous_state, current_state)
                #match['ticks'].append(changed_state)
                #previous_state = current_state
                match['ticks'].append(current_state)

                #Check if the game is over
                if self.is_complete():
                    match['status'] = 'Finished'
                    match['winners'] = self.get_winners()
                    break

        #Return the output of the game
        return match

    def get_changed_state(self, previous_state, current_state):
        """
        Work out the changes between the previous game state and the current game state
        """
        raise Exception('TODO')

    """
    Everything under this line must be overridden by real game classes
    """

    def initialise_teams(self, team_classes):
        """
        Ensure the teams are created and are valid (e.g. stats are in correct ranges)
        Return an error message or None
        """
        raise Exception('Games must override the initialise_teams method!')

    def run_tick(self):
        """
        Run one tick of this game
        This method must return a dictionary which is compared to the previous
        dictionary to find any changes to the game state
        """
        raise Exception('Games must override the run_tick method!')

    def get_constant_state(self):
        """
        Return a dictionary of any game state which remains constant.
        """
        raise Exception('Games must override the get_constant_state method!')

    def get_tick_state(self):
        """
        Return a dictionary of the current game state.
        This is compared to the previous game state to find changes which
        will be persisted
        """
        raise Exception('Games must override the get_tick_state method!')

    def is_complete(self):
        """
        Determine if this game is complete
        """
        raise Exception('Games must override the is_complete method!')

    def get_winners(self):
        """
        Determine who (if anyone) won this game
        """
        raise Exception('Games must override the get_winners method!')
