from tanks import game

#Maintain this manually
GAME_DICT = {
    'tanks': game.TankGame,
}

#Auto generate this
GAME_LIST = []
for id in GAME_DICT:
    GAME_LIST.append({
        'id': id,
        'name': GAME_DICT[id].name,
        'description': GAME_DICT[id].description,
    })
