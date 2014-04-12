import cherrypy

from team_not_found import database as db
from team_not_found import games


def get_teams(game_id=None):
    """
    """
    # Get all teams
    teams = db.Session.query(
        db.Team
    )

    # Filter for the game
    if game_id:
        teams = teams.filter(
            db.Team.game == game_id
        )

    # Apply necessary filtering
    if not cherrypy.request.user.is_admin:
        #Current user is not an admin so they only see yours & public
        teams = teams.filter(
            db.sa.or_(
                db.Team.is_public == True,
                db.Team.creator == cherrypy.request.user
            )
        )

    # Order them nicely
    teams = teams.order_by(
        db.Team.name
    )

    return teams

def get_split_teams(teams):
    """
    Split teams into yours, public & others
    """
    your_teams = []
    public_teams = []
    other_teams = []
    user_uuid = cherrypy.request.user.uuid
    for team in teams:
        #Get the latest team_file
        team_file = team.get_team_file()
        #Create the team lists
        team_dict = {
            'game': games.GAME_DICT[team.game].name,
            'team_uuid': team.uuid,
            'team_name': team.name,
            'team_file_uuid': team_file.uuid,
            'team_file_version': team_file.version,
        }
        if team.is_public:
            public_teams.append(team_dict)
        elif team.creator == user_uuid:
            your_teams.append(team_dict)
        else:
            other_teams.append(team_dict)

    return {
        'your_teams': your_teams,
        'public_teams': public_teams,
        'other_teams': other_teams,
    }

def get_team_sections(teams):
    """
    """
    if not teams:
        return []
    split_teams = get_split_teams(teams)
    return [
        {
            'type': 'Your Teams',
            'teams': split_teams['your_teams'],
        },
        {
            'type': 'Public Teams',
            'teams': split_teams['public_teams'],
        },
        {
            'type': 'Other Teams',
            'teams': split_teams['other_teams'],
        },
    ]
