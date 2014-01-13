var AIs = [];
var DIR = {
    N : 0/8 * 2*Math.PI,
    NE: 1/8 * 2*Math.PI,
    E : 2/8 * 2*Math.PI,
    SE: 3/8 * 2*Math.PI,
    S : 4/8 * 2*Math.PI,
    SW: 5/8 * 2*Math.PI,
    W : 6/8 * 2*Math.PI,
    NW: 7/8 * 2*Math.PI
};
var DEBUG = true;

var STAT_MIN = {
    ACCELERATION: 0.1,
    SPEED: 0.1,
    SIGHT: 0.2,
    SHIELD: 0.1,
    HEALTH: 0.2,
    RELOAD: 1,
    FIREPOWER: 0.1
};

var STAT_MULT = {
    ACCELERATION: 1,
    SPEED: 10,
    SIGHT: 200,
    SHIELD: 10,
    HEALTH: 100,
    RELOAD: 10,
    FIREPOWER: 10000
};

var GRAVITY = -0.1;
var DAMAGE = 10;
