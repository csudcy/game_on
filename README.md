TeamNotFound
============

TNF is a multi-game simulator/challenge which allows users to upload teams which
can then compete against other teams.

Features:
  * Support for multiple games (only 1 so far though...)
  * Users can make as many teams as they want
  * Matches can be replayed at any time
  * Matches are played asynchronously
  * Don't un-GZip results files before returning to client

Cool stuff coming up:
  * Stream match results to the GZipFile to avoid memory issues
  * Tournaments
    * Best of 3
    * ? Bracketed?
    * ? All v all/matrix?
  * Online editor
    * Allow the code to be edited & immediately played
    * Jump straight to this after player creation
    * Start the code as the example file from the game
    * http://ace.c9.io/ looks pretty sweet
  * Better error reporting
  * User creation

Stuff I really should do:
  * Improve index page
    * Latest matches
    * ? Use game thumbnails?
  * Time bound on ticks
  * ? Sandboxing?
    * Looks really difficult in Python
    * Maybe run teams in a seperate process & communicate via sockets?
  * ? File versioning?
  * Remove inline styles
  * Match/team table/dir cleanup

Stuff which probably isnt needed anymore:
  * File uploads
  * Download example team file


TeamNotFound.Tanks
==================

A (fairly basic) 5-a-side tank simulation

Features:
  * User allocatable stats (max speed, sight, health, blast radius)
  * Team stats
  * TODO: Fill this in...
  * Play games until all projectiles finish exploding

Coming up:
  * Resize canvas with window
  * Max proofing
