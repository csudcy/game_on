$(document).ready(function() {
    //Load the data
    function load_data() {
        $.get(DATA_URL).success(
            function(data, result, jqxhr) {
                //We now have the match data

                //Show progress
                var pc = data.matches_played * 100.0 / data.matches.length;
                $('.progress_inner').css('width', pc+'%')

                //Show matches
                var match_template = $('.match_template'),
                    match_container = $('#match_container');
                match_container.empty();
                data.matches.forEach(function(match) {
                    var jqe = match_template.clone();
                    jqe.find('.team_1_name').text(match.team_1);
                    jqe.find('.team_2_name').text(match.team_2);
                    jqe.find('.match_link').attr('href', '/tnf/match/'+match.uuid+'/');
                    if (match.state == 'WAITING') {
                        jqe.css('background-color', '#faa');
                    } else if (match.state == 'PLAYING') {
                        jqe.css('background-color', '#fa5');
                    }
                    jqe.appendTo(match_container)
                        .removeClass('match_template')
                        .show();
                });

                //Show scores
                var scoreboard_template = $('.scoreboard_template'),
                    scoreboard_container = $('#scoreboard_container');
                scoreboard_container.empty();
                data.scoreboard.forEach(function(team) {
                    var jqe = scoreboard_template.clone();
                    jqe.find('.team_name').text(team.name);
                    jqe.find('.team_score').text(team.score);
                    jqe.appendTo(scoreboard_container)
                        .removeClass('scoreboard_template')
                        .show();
                });

                //Show some more info
                $('#matches_played').text(data.matches_played);
                $('#matches_total').text(data.matches.length);

                //Check we should reload
                if (data.matches_played < data.matches.length) {
                    setTimeout(load_data, 2500);
                }
            }
        ).error(
            function() {
                alert('Error loading tournament results!');
                window.location = GAME_INFO_URL;
            }
        );
    }

    load_data();
});
