Tanks
=====

A (fairly basic) 5-a-side tank simulation

TODO:
    Add create_date to match
        Order list by reverse
        Display on list
    Show match winner(s)
        List?
        Replay?
    Improve index page
        Latest matches
        ? Use game thumbnails?
    File uploads
    Download example team file
    Play matches asynchronously
    ? Play tournaments?
        Best of 3
        Bracketed
        All v all/matrix
    ? Online editor?
    ? File versioning?

TANKS TODO:
    Incorporate tank direction & speed when firing
    Check for victory
    Max proofing
    ? Show current target on UI?

AI TODO:
    Movement prediciton
    Keep spotters moving
    Danger close
    ? Run away from enemies?
        Turn back if they go out of sight though

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
