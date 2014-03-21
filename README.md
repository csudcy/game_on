Tanks
=====

A (fairly basic) 5-a-side tank simulation

TODO:
    Change backend to Python
    Implement web socket to send udpates to frontend
    Record web socket traffic to file for replays
    ? Keep track of matches and results?
    File uploads & versioning
    Download example team file
    ? Online editor

New DB structure:
    User
        UUID
        Username
        PasswordHash
        IsAdmin
    Game
        UUID
        Name
        Description
    GameFile
        UUID
        GameUUID
        Filename
    GameFileVersion
        UUID
        GameFileUUID
        Path
        CreateDate
    Player
        UUID
        GameUUID
        Name
        Description
        IsPublic
        CreatorUUID
    PlayerFile
        UUID
        PlayerUUID
        Filename
    PlayerFileVersion
        UUID
        PlayerFileUUID
        Path
        CreateDate
