import logging
import Queue
import threading
import time

from team_not_found import database as db


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
                self.run_match(match_uuid)
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
        #logging.debug('MatchProcessor %s. ...' % (self.index, match_uuid))
        match = db.Session.query(
            db.Match
        ).filter(
            db.Match.uuid == match_uuid
        ).one()

        #Check the match WAITING
        #logging.debug('MatchProcessor %s. ...' % (self.index, match_uuid))
        if match.state != 'WAITING':
            raise Exception('Trying to process a match (%s) which is not WAITING (%s)' % (match_uuid, match.state))

        #Mark the match as PLAYING
        #logging.debug('MatchProcessor %s. ...' % (self.index, match_uuid))
        match.state = 'PLAYING'
        db.Session.commit()

        #Load the team classes
        #logging.debug('MatchProcessor %s. ...' % (self.index, match_uuid))
        team_1_class = match.team_1.load_class()
        team_2_class = match.team_2.load_class()

        #Find the game
        #logging.debug('MatchProcessor %s. ...' % (self.index, match_uuid))
        from team_not_found import games
        game = games.GAME_DICT[match.game]

        #Run the game & stream it to file
        #logging.debug('MatchProcessor %s. ...' % (self.index, match_uuid))
        game_obj = game([team_1_class, team_2_class])
        with match.get_flo_writer() as match_flo:
            game_obj.run(match_flo)

        #Mark the match as PLAYED
        #logging.debug('MatchProcessor %s. ...' % (self.index, match_uuid))
        match.state = 'PLAYED'
        db.Session.commit()

    def stop(self):
        """
        Let this processor know it should stop running
        """
        logging.debug('MatchProcessor %s. Stopping...' % self.index)
        self.running = False
