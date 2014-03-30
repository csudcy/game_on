from Queue import Queue
import logging

import cherrypy

from .match_processor import MatchProcessor
from team_not_found import database as db

class MatchManager(cherrypy.process.plugins.SimplePlugin):
    match_queue = None
    match_processors = None

    def __init__(self, processor_count=2):
        """
        Startup & track the given number of threads
        """
        super(MatchManager, self).__init__(bus = cherrypy.engine)

        #Create the processors
        logging.debug('Starting %s match processors...' % processor_count)
        self.match_queue = Queue()
        self.match_processors = []
        for i in xrange(processor_count):
            mp = MatchProcessor(i, self.match_queue)
            self.match_processors.append(mp)

        #Subscribe to the bus
        self.subscribe()

    def start(self):
        """
        Start the threads for this manager
        """
        #Start the processors
        logging.debug('Starting all match processors...')
        for mp in self.match_processors:
            mp.start()

    def stop(self):
        """
        Tell all match_processors they should stop
        """
        #Start the processors
        logging.debug('Stopping all match processors...')
        for gp in self.match_processors:
            gp.stop()

    def exit(self):
        """
        Wait for all match_processors to stop
        """
        #Wait for the processors
        logging.debug('Joining all match processors...')
        for gp in self.match_processors:
            gp.join()

    def add_match(self, match):
        """
        Add the given match to the queue
        """
        self.match_queue.put(match)

    def add_matches(self, matches):
        """
        Add all the given matches to the queue
        """
        for match in matches:
            self.add_match(match)
