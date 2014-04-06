$(document).ready(function() {
    //Load the data
    function load_data() {
        $.get(DATA_URL).success(
            function(body, result, jqxhr) {
                //We now have the match data
                var data;
                try {
                    data = JSON.parse(body);
                } catch (e) {
                    alert('Error parsing tournament results!');
                    window.location = GAME_INFO_URL;
                    return;
                }
                console.log(data);
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
