//// Deal with play state
var PLAY_DIRECTIONS = {
        reverse: -1,
        pause: 0,
        forward: 1,
    },
    play_direction = 0,
    match;
function update_play_state_click() {
    update_play_state($(this));
}
function update_play_state(button) {
    $('#forward').css('background-color', '');
    $('#pause').css('background-color', '');
    $('#reverse').css('background-color', '');
    button.css('background-color', 'darkgray');
    play_direction = PLAY_DIRECTIONS[button.attr('id')];
}

function pause() {
    update_play_state($('#pause'));
}

//// Execution management
function get_interval() {
    return parseInt($('#interval').val());
}
function set_interval(interval) {
    $('#interval_display').text(interval);
    $('#interval').val(interval);
}

function get_tick() {
    return parseInt($('#tick').val());
}
function get_max_tick() {
    return match.tick_state.length - 1;
}
function set_tick(tick) {
    if (match === undefined) {
        return;
    }
    //Validate the requested tick
    var max_ticks = get_max_tick();
    tick = Math.min(Math.max(tick, 0), max_ticks);
    if (tick === 0 || tick === max_ticks) {
        pause();
    }

    //Update tick UI
    $('#tick_display').text(tick);
    $('#tick').val(tick);

    //Show the winner yet?
    if (tick === max_ticks) {
        $('#winner_wait').hide();
        $('#winner_show').show();
    }

    //Show team stats
    var tick_state = match.tick_state[tick];
    function show_team_stats(team) {
        var player_states = tick_state[team].players,
            team_health = 0,
            max_health = match.constant_state[team].max_health,
            player_count = match.constant_state[team].player_count;
        for (var i=0; i<player_count; i++) {
            //Find this players health
            var player_state = player_states[i];

            //Update the global stats
            team_health += player_state.health;

            //Show death
            var pg_header = $('.team_stats.'+team+' .player_health.player_'+i);
            if (player_state.is_dead) {
                pg_header.css('color', 'red');
            } else {
                pg_header.css('color', '');
            }

            //Show this players health
            var pg_inner = $('.team_stats.'+team+' .player_health.player_'+i+' .pg_vert_inner');
            pg_inner.css('top', (1 - player_state.health / max_health) * pg_inner.height());
        }
        //Show team health
        var pg_inner = $('.team_stats.'+team+' .team_health .pg_horz_inner');
        pg_inner.css('width', (team_health / (player_count * max_health)) * pg_inner.parent().width());
    }
    show_team_stats('team_1');
    show_team_stats('team_2');

    //Show the winner yet?
    if (tick === max_ticks) {
        $('#winner_wait').hide();
        $('#winner_show').show();
    }

    //Draw ze tick
    draw_current_tick();
}

function draw_current_tick() {
    if (match === undefined) {
        return;
    }
    //Make the canvas the right size/aspect
    var field = $('#field'),
        field_screen_w = field.width(),
        field_screen_h = field.height(),
        field_screen_r = field_screen_w / field_screen_h,
        board_w = match.constant_state.board.width,
        board_h = match.constant_state.board.height,
        board_ratio = board_w / board_h,
        field_pixel_h,
        field_pixel_w;

    if (field_screen_r < board_ratio) {
        //Field is talller/thinner than board
        //Use full width
        field_pixel_w = board_w;
        field_pixel_h = board_w / field_screen_r;
    } else {
        //Board is talller/thinner than field
        //Use full height
        field_pixel_w = board_h * field_screen_r;
        field_pixel_h = board_h;
    }

    $('#field').attr('width', field_pixel_w);
    $('#field').attr('height', field_pixel_h);

    //Draw everything!
    draw_board(
        $('#field')[0].getContext('2d'),
        match.constant_state,
        match.tick_state[get_tick()]
    );
}

//// Timer
var last_timer_render = new Date();
function timer() {
    if (play_direction !== 0) {
        //Only do anything when we're playing
        var now = new Date();
        if (now - last_timer_render >= get_interval()) {
            //Time to move!
            set_tick(get_tick() + play_direction);
            last_timer_render = now;
        }
    }
}
function start_timer() {
    setInterval(timer, 1);
}

function show_loading(txt) {
    /*
    Disable all controls and show the given message on the field
    */
    //Make sure we're not trying to do anything
    pause();

    //Disable the controls
    $('.controls button, #interval, #tick').attr('disabled', 'disabled');
    $('#interval').bind('input', function() {
        set_interval($(this).val());
    });

    var field = $('#field'),
        g = field[0].getContext('2d'),
        w = field.attr('width'),
        h = field.attr('height');

    //Gray the field
    g.fillStyle = 'gray';
    g.fillRect(0, 0, w, h);

    //Show the message
    if (txt) {
        g.font = '30px sans-serif';
        g.fillStyle = 'black';
        var text_w = g.measureText(txt).width;
        g.fillText(txt, (w-text_w)/2, h/2);
    }
}

function clear_loading() {
    /*
    Enable controls, assume something else will draw on the field
    */
    $('.controls button, #interval, #tick').attr('disabled', null);
}

//Load the data
function load_data(data_url, redirect_url) {
    //Easiest way to save the passed in params...
    function _load() {
        $.get(data_url).success(
            function(body, result, jqxhr) {
                //We now have the match data
                var data;
                try {
                    data = JSON.parse(body);
                } catch (e) {
                    alert('Error parsing replay file!');
                    if (redirect_url) {
                        window.location = redirect_url;
                    }
                    return;
                }

                if (data.state !== undefined) {
                    //The match is not finished yet
                    //Let the user know
                    show_loading('Match is ' + data.state + '...');

                    //Then try again in a second
                    setTimeout(load_data, 1000);
                    return;
                }

                //Otherwise, this match is ready to go!
                match = data;

                //Show some info from the match
                $('#tick').attr('max', get_max_tick());
                $('#tick_max_display').text(get_max_tick());
                $('.team_1_name').text(match.constant_state.team_1.name);
                $('.team_2_name').text(match.constant_state.team_2.name);
                $('.team_1 .team_name').text(match.constant_state.team_1.name);
                $('.team_2 .team_name').text(match.constant_state.team_2.name);
                if (match.winners === undefined || match.winners === null || match.winners.length === 0) {
                    $('#winner_none').show();
                } else if (match.winners.length === 2) {
                    $('#winner_draw').show();
                } else {
                    $('#winner_' + match.winners[0]).show();
                }

                //Show some team colours
                $('.team_1 .pg_vert_inner, .team_1 .pg_horz_inner').css(
                    'background-color',
                    match.constant_state.team_1.effect_colour.replace('{alpha}', '1.0')
                )
                $('.team_2 .pg_vert_inner, .team_2 .pg_horz_inner').css(
                    'background-color',
                    match.constant_state.team_2.effect_colour.replace('{alpha}', '1.0')
                )

                //Hide the loading div
                clear_loading();

                //Show the first frame!
                set_tick(0);
                start_timer();
            }
        ).error(
            function() {
                alert('Error loading replay file!');
                if (redirect_url) {
                    window.location = redirect_url;
                }
            }
        );
    }

    //Show that we are loading
    show_loading('Loading...');

    //Do it, do it nao!
    _load();

    // Make sure we start in the right state
    $('#winner_wait').show();
    $('#winner_show').hide();
    pause();
}


$(document).ready(function() {
    //// Bind playback control handlers
    $('#start').click(function() {
        pause();
        set_tick(0);
    });

    $('#forward').click(update_play_state_click);

    $('#step_left').click(function() {
        pause();
        set_tick(get_tick() - 1);
    });

    $('#pause').click(update_play_state_click);

    $('#step_right').click(function() {
        pause();
        set_tick(get_tick() + 1);
    });

    $('#reverse').click(update_play_state_click);

    $('#end').click(function() {
        pause();
        set_tick(get_max_tick());
    });

    //// Bind other interaction handlers
    $('#interval').bind('input', function() {
        set_interval($(this).val());
    });

    $('#tick').bind('input', function() {
        pause();
        set_tick($(this).val());
    });

    set_interval(25);

    show_loading('No match loaded!');

    $(window).resize(function() {
        draw_current_tick();
    });
});
