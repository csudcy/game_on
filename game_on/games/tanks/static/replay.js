$(document).ready(function() {
    //// Deal with pause state
    var paused = true;

    function pause() {
        $('#pause').css('background-color', 'darkgray');
        $('#play').css('background-color', '');
        paused = true;
    }

    function play() {
        $('#pause').css('background-color', '');
        $('#play').css('background-color', 'darkgray');
        paused = false;
    }

    //// Bind interaction handlers
    $('#step_left').click(function() {
        pause();
        set_tick(get_tick() - 1);
    });

    $('#pause').click(pause);

    $('#play').click(play);

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
        var max_ticks = parseInt($('#tick').attr('max'));
        tick = Math.min(Math.max(tick, 0), max_ticks);
        $('#tick_display').text(tick);
        $('#tick').val(tick);
        render_tick();
    }

    //// Timer
    var last_timer_render = new Date();
    function timer() {
        if (!paused) {
            //Only do anything when we're playing
            var now = new Date();
            if (now - last_timer_render >= get_interval()) {
                //Time to move!
                set_tick(get_tick() + 1);
                last_timer_render = now;
            }
        }
    }
    setInterval(timer, 1);

    //// Rendering
    var match;
    var container = $('#field')[0];
    function render_tick() {
        if (match === undefined) {
            return;
        }
        draw_board(
            container.getContext('2d'),
            match.constant_state,
            match.tick_state[get_tick()]
        );
    }

    //// Make sure we start in the right state
    pause();
    set_interval(100);
    set_tick(0);

    //Load the data
    $.get(DATA_URL).success(
        function(body, result, jqxhr) {
            //We now have the match data
            match = JSON.parse(body);
            //console.log(match);

            //Show some info from the match
            $('#tick').attr('max', match.tick_count-1);
            $('#tick_max_display').text(match.tick_count-1);
            $('#field').attr('width', match.constant_state.board.width);
            $('#field').attr('height', match.constant_state.board.height);
            $('#team_1').text(match.constant_state.team_1.name);
            $('#team_2').text(match.constant_state.team_2.name);

            //Hide the loading div
            $('#loading').hide();

            //Show the first frame!
            render_tick();
        }
    ).error(
        function() {
            alert('Error loading replay file!');
            window.location = MATCH_LIST_URL;
        }
    );
});
