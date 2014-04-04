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


def start_match(game_id, team_1_uuid, team_2_uuid, user, tournament=None):
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
        tournament = tournament,
    )
    db.Session.add(match)

    #Save to db
    db.Session.commit()

    #Add to the match_manager
    match_manager.add_match(match.uuid)

    #Return the match so the callee knows what was created
    return match



def start_tournament(game_id, teams, tournament_type, best_of, user):
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
    team_objs = db.Session.query(
        db.Team
    ).filter(
        db.Team.uuid in teams
    )
    for team in team_objs:
        tournament.teams.append(team)

    #Save to db
    db.Session.commit()

    #Start the matches
    if tournament_type == 'matrix':
        #Matrix tournament - All v. all
        for t1 in teams:
            for t2 in teams:
                if t1 == t2:
                    continue
                for i in xrange(best_of):
                    start_match(game_id, t1, t2, user, tournament=tournament)
    else:
        raise Exception('Unknown tournament type "%s"!' % tournament_type)

    #Return the tournament so the callee knows what was created
    return tournament

"""
class Tournament(ModelBase, Base):
    creator_uuid = sa.Column(sa.String(36), sa.ForeignKey('user.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    creator = sa_orm.relationship('User', backref=backref('tournaments', passive_deletes=True, cascade="all"))

    teams = sa_orm.relationship('Team', secondary='tournamentteam', backref='tournaments')


class TournamentTeam(ModelBase, Base):
    tournament_uuid = sa.Column(sa.String(36), sa.ForeignKey('tournament.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    tournament = sa_orm.relationship('Tournament', backref=backref('tournament_teams', passive_deletes=True, cascade="all"))
    team_uuid = sa.Column(sa.String(36), sa.ForeignKey('team.uuid', onupdate="CASCADE", ondelete="CASCADE"), nullable=False)
    team = sa_orm.relationship('Team', backref=backref('tournament_teams', passive_deletes=True, cascade="all"))

"""
