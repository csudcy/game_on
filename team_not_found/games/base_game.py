import json

class BaseGame(object):
    """
    """
    #A short string identifier for this game
    id = None

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

    #The folder where static files for this game can be found (optional)
    """
    The static folder must have at least:
      replay_match.html
      replay_team_edit.html
      thumbnail.png
    Both html pages are provided with {{static_url}} so tehy can load any other
    files (js, css, images) they want to from their static folder.
    Both html pages must provide a javascript function used to initiate
    match replay: load_replay(data_url, redirect_url (optional))
    """
    static_folder = None

    #The jinja2 environment used for rendering UIs for this game
    jinja2_env = None

    def __init__(self, team_classes):
        if self.name is None:
            raise Exception(
                'You must define a name attribute on the game "{name}"!'.format(
                    name = self.name,
                ))
        if self.base_team is None:
            raise Exception(
                'You must define a base_team attribute on the game "{name}"!'.format(
                    name = self.name,
                ))
        if self.jinja2_env is None:
            raise Exception(
                'You must define a jinja2_env attribute on the game "{name}"!'.format(
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

    def run(self, match_flo):
        """
        Run this game until it ends
        A summary of the match in the folling format is written the match_flo:
            {
                'status': 'State of the game',
                'winners': ['team_1', 'team_2'],
                    (multiple winners => draw)
                'constant_state': {
                    <return of get_constant_state>
                },
                'tick_state': [
                    {
                        <return of get_tick_state>
                    },
                    ...
                ]
            }
        @return: Match winners
        """
        #Initialise the return structure
        match = {
            'status': None,
            'winners': None,
            'constant_state': None
        }

        #Not really a nice way to do streaming JSON in Python so we'll be
        #hacky as fuck...
        match_flo.write('{"tick_state": [')

        #Initialise the game
        error = self.initialise(self.team_classes)
        if error:
            match['status'] = 'Error - team init failed: %s' % error
        else:
            #Populate the constant state info
            match['constant_state'] = self.get_constant_state()

            #Tick until the game ends
            tick_count = 0
            previous_state = self.get_tick_state()
            match_flo.write(json.dumps(previous_state))
            while (True):
                #Check if we have run too many ticks
                if tick_count >= self.max_ticks:
                    match['status'] = 'Finished (Too many ticks)'
                    break
                tick_count += 1

                #Run a tick
                self.run_tick()

                #Get the changed game state
                current_state = self.get_tick_state()
                match_flo.write(',')
                match_flo.write(json.dumps(current_state))

                #Check if the game is over
                if self.is_complete:
                    match['status'] = 'Finished'
                    match['winners'] = self.get_winners()
                    break

        #Continuing to be hacky as fuck...
        #Close the list of tick_state
        match_flo.write('],')

        #Convert what we have so far into JSON
        match_json = json.dumps(match)

        #Remove the leading {
        match_json = match_json[1:]

        #Write the match_json to the match_flo
        match_flo.write(match_json)

        #Yay, hacky JSON streaming is complete!

        return match['winners']


    ##########################################################################
    ##########################################################################
    #   Everything under this line must be overridden by real game classes
    ##########################################################################
    ##########################################################################

    @classmethod
    def get_example_team_file(self):
        """
        Get the example team file used as the basis for all new teams
        @return: The contents of the example team file
        """
        raise Exception('Games must override the get_example_team_file method!')

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
        raise Exception('Games must override the get_example_teams method!')

    def initialise(self, team_classes):
        """
        Initialise this game. This includes ensure the teams are created and
        validated (e.g. stats are in correct ranges).
        Return an error message or None
        """
        raise Exception('Games must override the initialise method!')

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

    @property
    def is_complete(self):
        """
        Determine if this game is complete
        """
        raise Exception('Games must override the is_complete property!')

    def get_winners(self):
        """
        Determine who (if anyone) won this game
        """
        raise Exception('Games must override the get_winners method!')
