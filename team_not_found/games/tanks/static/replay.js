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
        //Validate the requested tick
        var max_ticks = get_max_tick();
        tick = Math.min(Math.max(tick, 0), max_ticks);
        if (tick === 0 || tick === max_ticks) {
            pause();
        }
        var tick_state = match.tick_state[tick];

        //Update tick UI
        $('#tick_display').text(tick);
        $('#tick').val(tick);

        //Show team stats
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

        //Draw everything!
        draw_board(
            field_container.getContext('2d'),
            match.constant_state,
            tick_state
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
    function load_data() {
        $.get(DATA_URL).success(
            function(body, result, jqxhr) {
                //We now have the match data
                var data;
                try {
                    data = JSON.parse(body);
                } catch (e) {
                    alert('Error parsing replay file!');
                    window.location = GAME_INFO_URL;
                    return;
                }

                if (data.state !== undefined) {
                    //The match is not finished yet
                    //Let the user know
                    $('#loading_text').text('Match is ' + data.state + '...');

                    //Then try again in a second
                    setTimeout(load_data, 1000);
                    return;
                }

                //Otherwise, this match is ready to go!
                match = data;

                //Show some info from the match
                $('#tick').attr('max', get_max_tick());
                $('#tick_max_display').text(get_max_tick());
                $('#field').attr('width', match.constant_state.board.width);
                $('#field').attr('height', match.constant_state.board.height);
                $('.team_name.team_1').text(match.constant_state.team_1.name);
                $('.team_name.team_2').text(match.constant_state.team_2.name);
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
                $('#loading').hide();

                //Show the first frame!
                set_tick(0);
                start_timer();
            }
        ).error(
            function() {
                alert('Error loading replay file!');
                window.location = GAME_INFO_URL;
            }
        );
    }
    load_data();
});
