import cherrypy

from team_not_found import database as db


def get_tournaments(game_id=None):
    """
    """
    # Get all tournaments
    tournaments = db.Session.query(
        db.Tournament
    )

    # Filter for the game
    if game_id:
        tournaments = tournaments.filter(
            db.Tournament.game == game_id
        )

    # Apply necessary filtering
    if not cherrypy.request.user.is_admin:
        #Current user is not an admin so they only see yours & your teams
        tournaments = tournaments.join(
            db.TournamentTeamFile
        ).join(
            db.TeamFile
        ).join(
            db.Team
        ).filter(
            db.sa.or_(
                db.Tournament.creator == cherrypy.request.user,
                db.Team.creator == cherrypy.request.user,
            )
        )

    # Order them nicely
    tournaments = tournaments.order_by(
        db.Tournament.create_date
    )

    return tournaments


def get_split_tournaments(tournaments):
    """
    Split tournaments into yours, your teams & others
    """
    your_tournaments = []
    your_team_tournaments = []
    other_tournaments = []
    user_uuid = cherrypy.request.user.uuid
    for tournament in tournaments:
        tournament_dict = {
            'tournament_uuid': tournament.uuid,
        }
        if tournament.creator_uuid == user_uuid:
            your_tournaments.append(tournament_dict)
        elif tournament.team_files.has(creator_uuid == user_uuid):
            your_team_tournaments.append(tournament_dict)
        else:
            other_tournaments.append(tournament_dict)

    return {
        'your_tournaments': your_tournaments,
        'your_team_tournaments': your_team_tournaments,
        'other_tournaments': other_tournaments,
    }

def get_tournament_sections(tournaments):
    """
    """
    if not tournaments:
        return []
    split_tournaments = get_split_tournaments(tournaments)
    return [
        {
            'type': 'Your Tournaments',
            'tournaments': split_tournaments['your_tournaments'],
        },
        {
            'type': 'Your Team Tournaments',
            'tournaments': split_tournaments['your_team_tournaments'],
        },
        {
            'type': 'Other Tournaments',
            'tournaments': split_tournaments['other_tournaments'],
        },
    ]
