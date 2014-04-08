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
        exec: save
    });
    editor.commands.addCommand({
        name: 'save_execute',
        bindKey: {win: 'F5',  mac: 'F5'},
        exec: save_execute
    });

    //Bind some click handlers
    $('#save').click(save);
    $('#save_execute').click(save_execute);

    function load_versions() {
        console.log('TODO: load_versions');
        //VERSIONS_URL
    }
    load_versions();

    function load_code(version) {
        $.get(CODE_URL, {'version': version}).success(
            function(body, result, jqxhr) {
                //Show the code in the editor
                editor.setValue(body.code);
                editor.gotoLine(0);
            }
        ).error(
            function() {
                alert('Error loading replay file!');
                window.location = GAME_INFO_URL;
            }
        );
    }
    load_code();

    function save() {
        console.log('TODO: save');
    }

    function save_execute() {
        console.log('TODO: save_execute');
    }
});
