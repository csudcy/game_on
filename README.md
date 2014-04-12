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
  * Stream match results to the GZipFile to avoid memory issues
  * Tournaments
  * Online team editing using http://ace.c9.io/

Cool stuff coming up:
  * Team creation
    * Jump straight to online editor after team creation
    * Allow the code to be edited & immediately played
    * Start the code as the example file from the game
  * Better error reporting
    * Catch errors & store on matches
    * Allow admins to replay
    * Ensure match_processor never stops
  * User creation
  * Tournaments
    * NAMES!
    * Best of 3
    * ? Bracketed?
    * ? All v all/matrix?

Stuff I really should do:
  * Link to team edit from match replay
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
    * Dont do this automatically
    * Allow admins to replay matches where the file doesnt exist
    * Dont show them to non-admins?
      * Could lead to much file checking?

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
