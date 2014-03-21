Tanks
=====

A (fairly basic) 5-a-side tank simulation

TODO:
    File uploads & versioning
    Download example team file
    ? Online editor
    Play matches asynchronously
    ? Play tournaments? Bracketed, all v all/matrix

TANKS TODO:
    Movement prediciton
    Incorporate tank direction & speed when firing
    Check for victory
    Max proofing

TANKS TO-REDO:
    Show current target on UI
    Health


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
