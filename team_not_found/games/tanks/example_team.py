"""
Example implementation of a player for TNF.Tanks!

The Basics
==========

This is a top down 5-a-side tank simulation. You position your tanks initially,
tell them what direction to move in, what speed to move at, what direction to point
their turret in and what elevation to shoot at. Enjoy!



Initialising players
====================

This is done via the init_players method below (see method for parameters and descriptions).
When initialising players, there are several variables you set:
  * Position - You provide x & y coordinates of where your tank should start on
    the field (within a given bounding box).
  * Stats - You control 4 aspects of your tank:
    * Health - How much health your tank starts with. More is better.
    * Speed - The maximum speed of your tank (acceleration is constant). Your
      initial speed is always 0.
    * Sight - How far your tank can "see". Only enemy locations which can be seen
      are reported when playing.
    * Blast Radius - How large an area is affected by projectile blasts. Ddamage
      is constant; increasing blast radius increases the chance of a tank being
      hit by the blast.
    You have upto 100 points to assign as you wish between the 4 stats.
  * Tank Direction - initially, you can face whatever direction you want. After
    that, changing tank direction takes time.
  * Turret Direction - initially, your turret can face whatever direction you want.
    After that, changing turret direction takes time. Turret direction is relative
    to tank direction.



Controlling players
===================

This is done via the run_tick method below (see method for parameters and descriptions).
These are the available mathods/properties on players:


Utility methods
---------------

player.angle_to(x, y)
    Calculate the angle (in radians) from player to (x,y).
player.distance_to(x, y)
    Calculate the distance (in pixels) from player to (x,y).
player.calculate_firing_angle(distance)
    Calculate the elevation angle required to fire a projectile <distance> pixels.


Position & Movement
-------------------

player.x & player.y
    Gives the current location of the player.
player.set_speed(v)
    Set the speed you want the player to move at. The player will accelerate/decelerate
    until the desired speed is achieved (unless the desired speed is over the players
    top speed when they will move at top speed).
player.set_direction(radians)
    Set the direction you want the player to face. The player will gradually turn
    until they are facing the desired direction.
player.direction.is_complete
    If the player is facing the desired direction.
player.set_target(x, y, r=10)
    Set a target for the player & a radius to stay in. The player will move
    constantly (unless you set_speed(0) but will try to keep within r distance
    from (x,y).
player.target_x & player.target_y
    Gives the current target location set for this player.
player.in_target
    Returns true if the player is within r distance from (target_x, target_y)
    (see player.set_target).


Firing
------

player.set_turret_direction(radians)
    Set the direction you want the players turret to face (relative to the tank
    direction). The turret will gradually turn to face the desired direction.
player.turret_direction.is_complete
    If the players turret is facing the desired direction.
player.can_fire
    If the player can currently fire. Reload time between shots is constant.
player.fire(elevation)
    Fire a projectile at the given elevation (elevation changes are instant) in
    the current turret direction.



General notes
=============

Blasts damage everything, not just opponents!

Directions:
    East  0
    South Pi/2
    West  Pi
    North 3Pi/2
"""

import random

from team_not_found.games.tanks import external


class Team(external.ExternalTeam):
    def init_players(self, PlayerClass, board_width, board_height, min_x, max_x, min_y, max_y, enemy_direction):
        """
        Initalise your players
        @param PlayerClass: The class used to create players
        @param board_width: The width of the board
        @param board_height: The height of the board
        @param min_x: The minimum x position you may place a player at
        @param max_x: The maximum x position you may place a player at
        @param min_y: The minimum y position you may place a player at
        @param max_y: The maximum y position you may place a player at
        @return: List of 5 instances of PlayerClass

        PlayerClass expects these keyword arguments:
            # Player position:
            x = num, # range: min_x-max_x
            y = num, # range: min_y-max_y
            # Player directions:
            direction = num, # range: 0-2*Pi
            turret_direction = num, # range: 0-2*Pi
            # Player stats:
            speed = num, # range: 0-1
            sight = num, # range: 0-1
            health = num, # range: 0-1
            blast_radius = num, # range: 0-1
        Note: The sum of speed, sight, health & blast_radius must be <= 100
        """
        # We need these later...
        self.board_width = board_width
        self.board_height = board_height

        # Initialise the players
        players = []
        x = (min_x + max_x) / 2
        y_step = (max_y - min_y) / 4
        for i in xrange(5):
            # Initialise another player
            player = PlayerClass(
                x=x,
                y=min_y + i * y_step,
                direction=enemy_direction,
                turret_direction=enemy_direction,
                speed=25,
                sight=25,
                health=25,
                blast_radius=25,
            )

            # Target a random place on the board
            self.set_random_target(player)

            # Add this player to the list of players
            players.append(player)

        # Return the list of players to the game
        return players

    def set_random_target(self, player):
        # Assign a random target to the given player
        player.set_target(
            random.randint(0, self.board_width),
            random.randint(0, self.board_height),
        )

    def run_tick(self, live_players, seen):
        """
        Work out what you want your team to do for the next tick
        @param: live_players A list of your players which are still alive
        @param: seen A list of {x:x, y:y} of seen enemy players
        """
        # We want to move around
        for player in live_players:
            # Check if this player has reached its target
            if player.in_target:
                #It has! Assign a new random target
                self.set_random_target(player)
