import cherrypy

from team_not_found import database as db
from team_not_found import games


def get_matches(game_id=None):
    """
    """
    # Get all matches
    matches = db.Session.query(
        db.Match
    ).filter(
        db.Match.tournament == None,
    )

    # Filter for the game
    if game_id:
        matches = matches.filter(
            db.Match.game == game_id
        )

    # Apply necessary filtering
    if not cherrypy.request.user.is_admin:
        #Current user is not an admin so they only see yours & your teams
        team_file_1 = db.sa_orm.aliased(db.TeamFile)
        team_file_2 = db.sa_orm.aliased(db.TeamFile)
        team_1 = db.sa_orm.aliased(db.Team)
        team_2 = db.sa_orm.aliased(db.Team)
        matches = matches.join(
            team_file_1,
            db.Match.team_file_1
        ).join(
            team_file_2,
            db.Match.team_file_2
        ).join(
            team_1,
            team_file_1.team
        ).join(
            team_2,
            team_file_2.team
        ).filter(
            db.sa.or_(
                db.Match.creator == cherrypy.request.user,
                team_1.creator == cherrypy.request.user,
                team_2.creator == cherrypy.request.user,
            )
        )

    # Order them nicely
    matches = matches.order_by(
        db.Match.create_date.desc()
    )

    return matches


def get_split_matches(matches):
    """
    Split matches into yours, your teams & others
    """
    your_matches = []
    your_team_matches = []
    other_matches = []
    user_uuid = cherrypy.request.user.uuid
    for match in matches:
        match_dict = {
            'game': games.GAME_DICT[match.game].name,
            'match_uuid': match.uuid,
            'team_1_uuid': match.team_file_1.team.uuid,
            'team_1_name': match.team_file_1.team.name,
            'team_file_1_uuid': match.team_file_1.uuid,
            'team_file_1_version': match.team_file_1.version,
            'team_2_uuid': match.team_file_2.team.uuid,
            'team_2_name': match.team_file_2.team.name,
            'team_file_2_uuid': match.team_file_2.uuid,
            'team_file_2_version': match.team_file_2.version,
        }
        t1c_uuid = match.team_file_1.team.creator_uuid
        t2c_uuid = match.team_file_2.team.creator_uuid

        if match.creator_uuid == user_uuid:
            your_matches.append(match_dict)
        elif t1c_uuid == user_uuid or t2c_uuid == user_uuid:
            your_team_matches.append(match_dict)
        else:
            other_matches.append(match_dict)

    return {
        'your_matches': your_matches,
        'your_team_matches': your_team_matches,
        'other_matches': other_matches,
    }


def get_match_sections(matches):
    """
    """
    if not matches:
        return []
    split_matches = get_split_matches(matches)
    return [
        {
            'type': 'Your Matches',
            'matches': split_matches['your_matches'],
        },
        {
            'type': 'Your Team Matches',
            'matches': split_matches['your_team_matches'],
        },
        {
            'type': 'Other Matches',
            'matches': split_matches['other_matches'],
        },
    ]
