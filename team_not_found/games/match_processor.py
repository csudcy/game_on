import logging
import Queue
import threading
import time

from team_not_found import database as db
from team_not_found.cfg import config


class MatchProcessor(threading.Thread):
    """
    """
    def __init__(self, index, queue):
        """
        Initialise the game processor
        """
        super(MatchProcessor, self).__init__()
        self.index = index
        self.queue = queue

    def run(self):
        """
        Wait for a match_uuid in the queue then process it & save results in the database
        """
        #Startup...
        logging.debug('MatchProcessor %s. Started...' % self.index)
        self.running = True

        #Main processing loop
        while (self.running):
            try:
                #Try to get a match_uuid from the queue
                match_uuid = self.queue.get(True, 1)
            except Queue.Empty:
                #Nothing to do here, move along
                pass
            else:
                #Process the match
                logging.debug('MatchProcessor %s. Processing match %s...' % (self.index, match_uuid))
                start_time = time.time()
                try:
                    self.run_match(match_uuid)
                except Exception, ex:
                    logging.error('Error processing match: %s' % str(ex))
                end_time = time.time()
                diff_time = end_time - start_time
                logging.debug('MatchProcessor %s. Processing match %s done in %.2fs!' % (self.index, match_uuid, diff_time))

                #Let the queue know it was completed
                self.queue.task_done()
        logging.debug('MatchProcessor %s. Stopped!' % self.index)

    def run_match(self, match_uuid):
        """
        Process the given match
        """
        #Find the match
        match = db.Session.query(
            db.Match
        ).filter(
            db.Match.uuid == match_uuid
        ).one()

        #Check the match is WAITING
        if match.state != 'WAITING':
            raise Exception('Trying to process a match (%s) which is not WAITING (%s)' % (match_uuid, match.state))

        #Mark the match as PLAYING
        match.state = 'PLAYING'
        db.Session.commit()

        #Find the game
        from team_not_found import games
        game = games.GAME_DICT[match.game]

        try:
            #Load the team classes
            team_1_class = match.team_file_1.load_class()
            team_2_class = match.team_file_2.load_class()

            #Run the game & stream it to file
            game_obj = game([team_1_class, team_2_class])
            with match.get_flo_writer() as match_flo:
                winners = game_obj.run(match_flo)

            #Mark the match as PLAYED
            match.state = 'PLAYED'
            winners = winners or []
            match.team_1_won = 'team_1' in winners
            match.team_2_won = 'team_2' in winners
            db.Session.commit()
        except Exception, ex:
            #Get the traceback
            import traceback
            tb = traceback.format_exc(ex)

            #Attempt to clean it up
            try:
                #Find the first line with the team directory on it
                team_folder = config['team']['folder']
                if team_folder in tb:
                    tb_lines = tb.split('\n')
                    safe_lines = []
                    found_folder = False
                    for tb_line in tb_lines:
                        found_folder = found_folder or team_folder in tb_line
                        if found_folder:
                            safe_lines.append(tb_line)
                    tb = '\n'.join(safe_lines)
            except Exception, ex2:
                logging.error(ex2)

            try:
                #Make references to the team files nice
                tf1_name = '<%s v%s>' % (
                    match.team_file_1.team.name,
                    match.team_file_1.version,
                )
                tb = tb.replace(match.team_file_1.path, tf1_name)
            except Exception, ex2:
                logging.error(ex2)

            try:
                tf2_name = '<%s v%s>' % (
                    match.team_file_2.team.name,
                    match.team_file_2.version,
                )
                tb = tb.replace(match.team_file_2.path, tf2_name)
            except Exception, ex2:
                logging.error(ex2)


            #Mark the match as ERRORED
            match.state = 'ERRORED'
            match.error = tb
            db.Session.commit()

    def stop(self):
        """
        Let this processor know it should stop running
        """
        logging.debug('MatchProcessor %s. Stopping...' % self.index)
        self.running = False
