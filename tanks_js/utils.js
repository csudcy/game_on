//http://ejohn.org/blog/simple-javascript-inheritance/
/* Simple JavaScript Inheritance
 * By John Resig http://ejohn.org/
 * MIT Licensed.
 */
// Inspired by base2 and Prototype
(function(){
    var initializing = false, fnTest = /xyz/.test(function(){xyz;}) ? /\b_super\b/ : /.*/;

    // The base Class implementation (does nothing)
    this.Class = function(){};

    // Create a new Class that inherits from this class
    Class.extend = function(prop) {
        var _super = this.prototype;

        // Instantiate a base class (but only create the instance,
        // don't run the init constructor)
        initializing = true;
        var prototype = new this();
        initializing = false;

        // Copy the properties over onto the new prototype
        for (var name in prop) {
            // Check if we're overwriting an existing function
            prototype[name] = typeof prop[name] == "function" &&
                typeof _super[name] == "function" && fnTest.test(prop[name]) ?
                (function(name, fn){
                    return function() {
                        var tmp = this._super;

                        // Add a new ._super() method that is the same method
                        // but on the super-class
                        this._super = _super[name];

                        // The method only need to be bound temporarily, so we
                        // remove it when we're done executing
                        var ret = fn.apply(this, arguments);
                        this._super = tmp;

                        return ret;
                    };
                })(name, prop[name]) :
                prop[name];
        }

        // The dummy class constructor
        function Class() {
            // All construction is actually done in the init method
            if ( !initializing && this.init )
                this.init.apply(this, arguments);
        }

        // Populate our constructed prototype object
        Class.prototype = prototype;

        // Enforce the constructor to be what we expect
        Class.prototype.constructor = Class;

        // And make this class extendable
        Class.extend = arguments.callee;

        return Class;
    };
})();

function circle_bound(val) {
    while (val < -Math.PI) {
        val += 2*Math.PI;
    }
    while (val >= Math.PI) {
        val -= 2*Math.PI;
    }
    return val;
}

function angle_speed_to_xy(angle, speed) {
    return {
        x: speed * Math.cos(angle),
        y: speed * Math.sin(angle)
    };
}

var RateBoundVariable = Class.extend({
    init: function(current, rate, minimum, maximum) {
        this.current = current;
        this.target = current;
        this.last_diff = 0;
        this.rate = rate;
        this.minimum = minimum;
        this.maximum = maximum;
    },
    set_target: function(target) {
        if (this.minimum !== undefined) {
            target = Math.max(target, this.minimum);
        }
        if (this.maximum !== undefined) {
            target = Math.min(target, this.maximum);
        }
        this.target = target;
    },
    is_complete: function() {
        //return this.target == this.current;
        return Math.abs(this.target - this.current) < 0.1;
    },
    check_target_bounds: function(val) {
        /*
        Check this value is within the bounds of this variable
        */
        return val;
    },
    update: function() {
        if (!this.is_complete()) {
            this.last_diff = this.check_target_bounds(this.target - this.current);
            if (this.last_diff < 0) {
                this.last_diff = Math.max(this.last_diff, -this.rate);
            } else {
                this.last_diff = Math.min(this.last_diff, this.rate);
            }
            this.current = this.check_target_bounds(this.current + this.last_diff);
        } else {
            this.last_diff = 0;
        }
    }
});

var RateBoundDirection = RateBoundVariable.extend({
    set_target: function(target) {
        this.target = circle_bound(target);
    },
    check_target_bounds: circle_bound
});
