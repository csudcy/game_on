/*
TODO:
    Movement prediciton
    Incorporate tank direction & speed when firing
    Check for victory
    Improve controls
        Effect colour picker
    Make matches replayable?
*/

$(document).ready(function() {
    //Initialise the board
    function populate_dropdown(id) {
        var dd = $('#'+id);
        AIs.forEach(function(ai, index) {
            dd
                .append($('<option></option>')
                .attr('value', index)
                .text(ai.description)); 
        });
    }
    populate_dropdown('ai_1');
    populate_dropdown('ai_2');

    var timer_jqe = $('#time_display');
    var board = new Board(
        $('#field')[0], // container,
        5, // player_count,
        function(time) {
            timer_jqe.text(time);
        }, //update_timer
        function(paused) {
            if (paused) {
                $('#play_pause').text('Play');
            } else {
                $('#play_pause').text('Pause');
            }
        } //update_pause_state
    );
    reset();

    function reset() {
        //Start a new game
        board.reset(
            AIs[parseInt($('#ai_1').val())], // ai_1_class,
            AIs[parseInt($('#ai_2').val())] // ai_2_class,
        );
    }

    $('#reset').click(reset);

    $('#play_pause').click(function() {
        board.toggle_paused();
    });

    $('#step').click(function() {
        board.run(true);
    });

    $('#interval').change(function() {
        set_interval($(this).val());
    });

    function set_interval(interval) {
        $('#interval_display').text(interval);
        $('#interval').val(interval);
        $.cookie('interval', interval);
        board.set_interval(interval);
    }

    var interval = board.get_interval();
    $('#interval').val(interval);
    $('#interval_display').text(interval);
});
