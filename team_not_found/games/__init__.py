from .match_manager import MatchManager
from .tanks import game
from team_not_found import database as db


#Maintain this manually
GAME_DICT = {
    'tanks': game.TankGame,
}

#Auto generate this
GAME_LIST = []
for game_id in GAME_DICT:
    GAME_LIST.append({
        'id': game_id,
        'name': GAME_DICT[game_id].name,
        'description': GAME_DICT[game_id].description,
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
    for game_id in GAME_DICT:
        example_teams = GAME_DICT[game_id].get_example_teams()
        for example_team in example_teams:
            existing_teams = db.Session.query(
                db.Team
            ).filter(
                db.Team.path == example_team['path']
            )
            if existing_teams.count() == 0:
                team = db.Team(
                    game = game_id,
                    name = example_team['name'],
                    is_public = example_team.get('is_public', True),
                    path = example_team['path'],
                    creator = admin_user,
                )
                db.Session.add(team)
    db.Session.commit()


match_manager =  None
def initialise_manager():
    """
    Initialise the match manager which will run games in the background
    """
    global match_manager

    #Initialise the manager
    match_manager = MatchManager()

    #Deal with unplayed matches
    unplayed_matches = db.Session.query(
        db.Match
    ).filter(
        db.Match.state != 'PLAYED'
    )

    #Reset the unplayed_matches to WAITING
    unplayed_match_uuids = []
    for unplayed_match in unplayed_matches:
        unplayed_match.state = 'WAITING'
        unplayed_match_uuids.append(unplayed_match.uuid)
    db.Session.commit()

    #Populate the match_manager with unplayed_matches
    match_manager.add_matches(unplayed_match_uuids)


def start_match(game_id, team_1_uuid, team_2_uuid, user):
    """
    Create the match & add it to the manager
    """
    #Create the match
    match = db.Match(
        game = game_id,
        team_1_uuid = team_1_uuid,
        team_2_uuid = team_2_uuid,
        creator = user,
        state = 'WAITING',
    )

    #Save to db
    db.Session.add(match)
    db.Session.commit()

    #Add to the match_manager
    match_manager.add_match(match.uuid)

    #Return the match so the callee knows what was created
    return match
