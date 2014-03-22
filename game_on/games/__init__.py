from tanks import game

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

def initialise_games(admin_user):
    """
    Add any example teams from games to the database
    """
    from game_on import database as db
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
