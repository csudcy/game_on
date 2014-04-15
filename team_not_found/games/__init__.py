from .match_manager import MatchManager
from .tanks import game
from team_not_found import database as db


#Maintain this manually
GAMES = (
    game.TankGame,
)

#Auto generate this
GAME_LIST = []
GAME_DICT = {}
for game in GAMES:
    GAME_DICT[game.id] = game
    GAME_LIST.append({
        'id': game.id,
        'name': game.name,
        'description': game.description,
    })


def initialise(admin_user):
    """
    Initialise everything global related to games
    """
    initialise_games(admin_user)
    initialise_manager()


def initialise_games(admin_user):
    """
    Add any example teams from games to the database
    """
    from team_not_found import database as db
    for game in GAMES:
        example_teams = game.get_example_teams()
        for example_team in example_teams:
            existing_teams = db.Session.query(
                db.Team
            ).filter(
                db.Team.name == example_team['name']
            )
            if existing_teams.count() == 0:
                #Create the team
                team = db.Team(
                    game = game.id,
                    name = example_team['name'],
                    is_public = example_team.get('is_public', True),
                    creator = admin_user,
                )
                db.Session.add(team)

                #Read the example team file
                with open(example_team['path'], 'r') as f:
                    contents = f.read()

                #Add the file to the team
                team.add_file(contents)

    db.Session.commit()


match_manager =  None
def initialise_manager():
    """
    Initialise the match manager which will run games in the background
    """
    global match_manager

    #Initialise the manager
    match_manager = MatchManager()

    #Deal with playing matches
    playing_matches = db.Session.query(
        db.Match
    ).filter(
        db.Match.state == 'PLAYING'
    )

    #Reset the playing_matches to WAITING
    playing_match_uuids = []
    for playing_match in playing_matches:
        playing_match.state = 'WAITING'
        playing_match_uuids.append(playing_match.uuid)
    db.Session.commit()

    #Populate the match_manager with playing_matches
    match_manager.add_matches(playing_match_uuids)


def start_match(game_id, team_file_1_uuid, team_file_2_uuid, user, tournament=None):
    """
    Create the match & add it to the manager
    """
    #Create the match
    match = db.Match(
        game = game_id,
        team_file_1_uuid = team_file_1_uuid,
        team_file_2_uuid = team_file_2_uuid,
        creator = user,
        state = 'WAITING',
        tournament = tournament,
    )
    db.Session.add(match)

    #Save to db
    db.Session.commit()

    #Add to the match_manager
    match_manager.add_match(match.uuid)

    #Return the match so the callee knows what was created
    return match



def start_tournament(game_id, team_file_uuids, tournament_type, best_of, user):
    """
    Create the match & add it to the manager
    """
    #Create the tournament
    tournament = db.Tournament(
        game = game_id,
        tournament_type = tournament_type,
        best_of = best_of,
        creator = user,
    )
    db.Session.add(tournament)

    #Add teams to the tournament
    team_files = db.Session.query(
        db.TeamFile
    ).filter(
        db.TeamFile.uuid.in_(team_file_uuids)
    ).all()
    for team_file in team_files:
        tournament.team_files.append(team_file)

    #Save to db
    db.Session.commit()

    #Start the matches
    if tournament_type == 'matrix':
        #Matrix tournament - All v. all
        for tf1u in team_file_uuids:
            for tf2u in team_file_uuids:
                if tf1u == tf2u:
                    continue
                for i in xrange(best_of):
                    start_match(game_id, tf1u, tf2u, user, tournament=tournament)
    else:
        raise Exception('Unknown tournament type "%s"!' % tournament_type)

    #Return the tournament so the callee knows what was created
    return tournament
