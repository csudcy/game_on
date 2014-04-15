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
  * Team files are versioned
  * Users can signup & get sent email confirmations
  * Users can create teams

Bugs:
  * Sort out constant data for team replays
    * Team names shouldnt be stored in the file
    * Link to team edit from match replay
    * Team files shouldn't have names in (except for example teams)

Cool stuff coming up:
  * Better error reporting
    * ?Allow admins to replay ?
    * Deal with ERRORED matches in tournaments
  * Tournaments
    * NAMES!
    * Best of 3
    * ? Bracketed?
    * ? All v all/matrix?

Stuff I really should do:
  * Show game details on game info page
  * Limit email confirmation send times
  * Allow team name & is_public to be edited
  * ? Hide team edit matches from normal match lists?
  * Time bound on ticks
  * ? Sandboxing?
    * Looks really difficult in Python
    * Maybe run teams in a seperate process & communicate via sockets?
  * Remove inline styles
  * Match/team table/dir cleanup
    * Dont do this automatically
    * Allow admins to replay matches where the file doesnt exist
    * Dont show them to non-admins?
      * Could lead to much file checking?


TeamNotFound.Tanks
==================

A (fairly basic) 5-a-side tank simulation

Features:
  * User allocatable stats (max speed, sight, health, blast radius)
  * Team stats
  * TODO: Fill this in...
  * Play games until all projectiles finish exploding
  * Canvas resizes with window

Coming up:
  * Fix thread bug - I think tanks.player.Player.STATS is shared
  * Don't show projectiles over the field edge (but track them )
  * Max proofing
