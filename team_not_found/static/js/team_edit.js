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

    function save() {
        alert('save');
    }

    function save_execute() {
        alert('save_execute');
    }
});
