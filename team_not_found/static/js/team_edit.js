$(document).ready(function() {
    //Setup the editor
    var editor = ace.edit("editor");
    editor.setTheme("ace/theme/solarized_dark");
    editor.getSession().setMode("ace/mode/python");
    editor.setHighlightActiveLine(false);
    editor.setShowInvisibles(true);

    //Bind some shortcut handlers
    editor.commands.addCommand({
        name: 'save',
        bindKey: {win: 'Ctrl-S',  mac: 'Command-S'},
        exec: function(editor) {
            save();
        }
    });
    editor.commands.addCommand({
        name: 'save_execute',
        bindKey: {win: 'F5',  mac: 'F5'},
        exec: function(editor) {
            save(execute);
        }
    });

    //Bind some click handlers
    $('#save').click(function() {
        save();
    });
    $('#save_execute').click(function() {
        save(execute);
    });
    $('#versions').change(function() {
        if (save_is_enabled()) {
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
    function save_enable() {
        $('#save').removeAttr('disabled');
        $('#changed').show();
    }
    function save_disable() {
        $('#save').attr('disabled', 'disabled');
        $('#changed').hide();
    }
    function save_is_enabled() {
        return !$('#save').attr('disabled');
    }

    //Enable the save button when editor contents is changed
    editor.getSession().on('change', function(e) {
        save_enable();
    });

    //Alert the user if they try to leave when they have unsaved changes
    $(window).bind('beforeunload', function(){
        if (save_is_enabled()) {
            return 'You have unsaved changes; really leave?';
        }
    });

    var versions = [],
        current_version;
    function load_versions() {
        $.get(VERSIONS_URL).success(
            function(body, result, jqxhr) {
                //Save the list of versions
                versions = body;

                //Populate the version select
                var html = '';
                for (var version in versions) {
                    html += '<option value="'+version+'">'+version+'</option>';
                }
                $('#versions').html(html);

                if (current_version) {
                    //Update the UI
                    check_version();
                } else {
                    //Load the latest version
                    load_code();
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
        Update the UI depending on the current_version
        */
        //Show the current version on the UI
        $('#versions').val(current_version);
        $('#current_version').text(current_version);

        //Check we are still editing the latest version
        if (current_version !== versions[versions.length - 1]) {
            //Switch to readonly mode
            editor.setReadOnly(true);
            $('#read_only').show();
        } else {
            //We are editing the latest version of the code
            editor.setReadOnly(false);
            $('#read_only').hide();
        }
    }

    function load_code(version) {
        var get_data = {
            'version': version
        };
        $.get(CODE_URL, get_data).success(
            function(body, result, jqxhr) {
                //Record what version we are working on
                current_version = body.version;

                //Show the code in the editor
                editor.setValue(body.code);
                editor.gotoLine(0);

                //Update save state
                save_disable();

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
        var post_data = {
            'version': current_version,
            'code': editor.getValue()
        };
        $.post(CODE_URL, post_data).success(
            function(body, result, jqxhr) {
                //Record success
                save_disable();
                current_version = body.version;
                load_versions();

                //Call cb
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

    function execute(version) {
        console.log('TODO: execute');
    }

    //Kick everything off
    load_versions();
});
