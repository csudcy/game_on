$(document).ready(function() {
    //// Deal with play state
    var PLAY_DIRECTIONS = {
            reverse: -1,
            pause: 0,
            forward: 1,
        },
        play_direction = 0,
        field_container = $('#field')[0],
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

    //// Bind interaction handlers
    $('#step_left').click(function() {
        pause();
        set_tick(get_tick() - 1);
    });

    $('#forward').click(update_play_state_click);

    $('#pause').click(update_play_state_click);

    $('#reverse').click(update_play_state_click);

    $('#step_right').click(function() {
        pause();
        set_tick(get_tick() + 1);
    });

    $('#interval').change(function() {
        set_interval($(this).val());
    });

    $('#tick').change(function() {
        pause();
        set_tick($(this).val());
    });

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
    function set_tick(tick) {
        //Validate the requested tick
        var max_ticks = parseInt($('#tick').attr('max'));
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

        //Draw everything!
        draw_board(
            field_container.getContext('2d'),
            match.constant_state,
            match.tick_state[tick]
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

    //// Make sure we start in the right state
    pause();
    set_interval(25);

    //Load the data
    $.get(DATA_URL).success(
        function(body, result, jqxhr) {
            //We now have the match data
            match = JSON.parse(body);

            //Show some info from the match
            $('#tick').attr('max', match.tick_count-1);
            $('#tick_max_display').text(match.tick_count-1);
            $('#field').attr('width', match.constant_state.board.width);
            $('#field').attr('height', match.constant_state.board.height);
            $('#team_1').text(match.constant_state.team_1.name);
            $('#team_2').text(match.constant_state.team_2.name);
            if (!match.winners) {
                //Undefined or empty
                $('#winner_none').show();
            } else if (match.winners.length === 2) {
                $('#winner_draw').show();
            } else {
                $('#winner_' + match.winners[0]).show();
            }

            //Hide the loading div
            $('#loading').hide();

            //Show the first frame!
            set_tick(0);
            start_timer();
        }
    ).error(
        function() {
            alert('Error loading replay file!');
            window.location = MATCH_LIST_URL;
        }
    );
});
