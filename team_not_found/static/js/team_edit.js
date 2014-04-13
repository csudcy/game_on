$(document).ready(function() {
    //Setup the editor
    var editor = ace.edit("editor");
    editor.setTheme("ace/theme/solarized_dark");
    editor.getSession().setMode("ace/mode/python");
    editor.setHighlightActiveLine(false);
    editor.setShowInvisibles(true);

    //State variables
    var versions = [],
        current_info;

    //Bind some shortcut handlers
    editor.commands.addCommand({
        name: 'save',
        bindKey: {win: 'Ctrl-S',  mac: 'Command-S'},
        exec: function(editor) {
            save();
        }
    });
    editor.commands.addCommand({
        name: 'execute',
        bindKey: {win: 'F5',  mac: 'F5'},
        exec: function(editor) {
            execute();
        }
    });

    //Bind some click handlers
    $('#save').click(function() {
        save();
    });
    $('#execute').click(function() {
        execute();
    });
    $('#versions').change(function() {
        /*
        Listen for the version dropdown being changed & load the selected version
        */
        if (save_is_required()) {
            //There are unsaved changes
            if (!confirm('You have unsaved changes; really load old version?')) {
                //Reset selected version
                check_version()
                return;
            }
        }
        load_code($('#versions').val());
    });

    //Functions to help save state
    function save_set_enabled() {
        /*
        Check if the current editor code is the same as the last loaded/saved code
        */
        if (save_is_required()) {
            //Code has not changed, disable save button
            $('#save').attr('disabled', 'disabled');
            $('#changed').hide();
        } else {
            //Code has changed, enable save button
            $('#save').removeAttr('disabled');
            $('#changed').show();
        }
    }
    function save_is_required() {
        /*
        Check if a save is currently necessary
        */
        return editor.getValue() !== current_info.code;
    }

    //Enable the save button when editor contents is changed
    editor.getSession().on('change', function(e) {
        save_set_enabled();
    });

    //Alert the user if they try to leave when they have unsaved changes
    $(window).bind('beforeunload', function(){
        if (save_is_required()) {
            return 'You have unsaved changes; really leave?';
        }
    });

    function load_versions() {
        /*
        Populate the list of versions available for this team from the server.
        */
        $.get(VERSIONS_URL).success(
            function(body, result, jqxhr) {
                //Save the list of versions
                versions = body;

                //Populate the version select
                var html = '';
                versions.forEach(function(version) {
                    html += '<option value="'+version.team_file_uuid+'">'+version.team_file_version+'</option>';
                });
                $('#versions').html(html);

                if (current_info !== undefined) {
                    //Update the UI
                    check_version();
                } else {
                    //This is the first time we've loaded anything
                    //Load the (probably) latest version of the code
                    load_code(INITIAL_TEAM_FILE_UUID);
                }
            }
        ).error(
            function() {
                alert('Error loading versions!');
                //window.location = GAME_INFO_URL;
            }
        );
    }

    function check_version() {
        /*
        Update the UI depending on the current_info
        */
        //Show the current version on the UI
        $('#versions').val(current_info.team_file_uuid);
        $('#current_version').text(current_info.team_file_version);

        //Check we are still editing the latest version
        var latest_version = versions[versions.length - 1];
        if (!EDITABLE || current_info.team_file_uuid !== latest_version.team_file_uuid) {
            //Switch to readonly mode
            editor.setReadOnly(true);
            $('#read_only').show();
        } else {
            //We are editing the latest version of the code
            editor.setReadOnly(false);
            $('#read_only').hide();
        }
    }

    function load_code(team_file_uuid) {
        /*
        Load the given version of code for the current team.
        */
        var get_data = {
            'team_file_uuid': team_file_uuid
        };
        $.get(CODE_LOAD_URL, get_data).success(
            function(body, result, jqxhr) {
                //Record what we are working on
                current_info = body;

                //Show the code in the editor (this also updates save state)
                editor.setValue(body.code);
                editor.gotoLine(0);

                //Update the UI
                check_version();
            }
        ).error(
            function() {
                alert('Error loading code!');
                //window.location = GAME_INFO_URL;
            }
        );
    }

    function save(cb) {
        /*
        Save the latest code to the server
        */
        if (!save_is_required()) {
            //We don't need to save right now
            return;
        }
        var post_data = {
            'team_file_uuid': current_info.team_file_uuid,
            'code': editor.getValue()
        };
        $.post(CODE_SAVE_URL, post_data).success(
            function(body, result, jqxhr) {
                //Record success
                current_info = body;
                current_info.code = post_data.code;
                save_set_enabled();

                //Reload the versions list
                load_versions();

                //Call cb (if there is one)
                if (cb) {
                    cb();
                }
            }
        ).error(
            function() {
                alert('Error saving code!');
                //window.location = GAME_INFO_URL;
            }
        );
    }

    function execute() {
        /*
        Execute the current version of the code
        */
        if (save_is_required()) {
            if (confirm('Save changes before executing?')) {
                return save(execute);
            }
        }
        console.log('TODO: execute');
    }

    //Kick everything off
    load_versions();
});
