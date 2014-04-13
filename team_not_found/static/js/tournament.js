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
                    jqe.find('.team_1_name').text(match.team_1_name);
                    jqe.find('.team_file_1_version').text(match.team_file_1_version);
                    jqe.find('.team_file_1_edit').attr('href', '/tnf/team/edit/'+match.team_1_uuid+'/'+match.team_file_1_uuid+'/');
                    jqe.find('.team_2_name').text(match.team_2_name);
                    jqe.find('.team_file_2_version').text(match.team_file_2_version);
                    jqe.find('.team_file_2_edit').attr('href', '/tnf/team/edit/'+match.team_2_uuid+'/'+match.team_file_2_uuid+'/');
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
                    jqe.find('.team_name').text(team.team_name);
                    jqe.find('.team_version').text(team.team_file_version);
                    jqe.find('.team_edit').attr('href', '/tnf/team/edit/'+team.team_uuid+'/'+team.team_file_uuid+'/');
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
