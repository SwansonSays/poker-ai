import numpy as np


def build_combonations(cards, type):
    combos = []
    if(type == 0):
        for i in range(4):         
            if i == 0:
                for j in range(3):
                    if j == 0:
                        combos.append([cards[0] + "h", cards[1] + "d"])
                    elif j == 1:
                        combos.append([cards[0] + "h", cards[1] + "c"]) 
                    elif j == 2:
                        combos.append([cards[0] + "h", cards[1] + "s"])
            elif i == 1:
                    if j == 0:
                        combos.append([cards[0] + "d", cards[1] + "h"])
                    elif j == 1:
                        combos.append([cards[0] + "d", cards[1] + "c"]) 
                    elif j == 2:
                        combos.append([cards[0] + "d", cards[1] + "s"])
            elif i == 2:
                for j in range(3):
                    if j == 0:
                        combos.append([cards[0] + "c", cards[1] + "d"])
                    elif j == 1:
                        combos.append([cards[0] + "c", cards[1] + "h"]) 
                    elif j == 2:
                        combos.append([cards[0] + "c", cards[1] + "s"])
            elif i == 3:
                for j in range(3):
                    if j == 0:
                        combos.append([cards[0] + "s", cards[1] + "d"])
                    elif j == 1:
                        combos.append([cards[0] + "s", cards[1] + "c"]) 
                    elif j == 2:
                        combos.append([cards[0] + "s", cards[1] + "h"])
    elif(type == 1):
        for i in range(4):
            if i == 0:
                combos.append([cards[0] + "h", cards[1] + "h"])
            elif i == 1:
                combos.append([cards[0] + "d", cards[1] + "d"])
            elif i == 2:
                combos.append([cards[0] + "c", cards[1] + "c"])
            elif i == 3:
                combos.append([cards[0] + "s", cards[1] + "s"])
    elif(type == 2):
        for i in range(6):
            if i == 0:
                combos.append([cards[0] + "h", cards[1] + "d"])
            elif i == 1:
                combos.append([cards[0] + "h", cards[1] + "c"])
            elif i == 2:
                combos.append([cards[0] + "h", cards[1] + "s"])
            elif i == 3:
                combos.append([cards[0] + "d", cards[1] + "c"])       
            elif i == 4:
                combos.append([cards[0] + "d", cards[1] + "s"])
            elif i == 5:
                combos.append([cards[0] + "c", cards[1] + "s"])    

    combos = np.array(combos).flatten()
    return combos

utg_range = [
    ["A","A", 2],["K","K", 2],["Q","Q", 2],["J","J", 2],["T","T", 2],["9","9", 2],["8","8", 2],["7","7", 2],
    ["A","K", 1],["A","Q", 1],["A","JK", 1],["A","T", 1],["A","9", 1],["A","8", 1],["A","7", 1],["A","6", 1],["A","5", 1],["A","4", 1],["A","3", 1],
    ["K","Q",1],["K","J",1],["K","T",1],["K","9",1],
    ["Q","J",1],["Q","T",1],
    ["J","T",1],
    ["T","9",1],
    ["A","K",0],["A","Q",0],["A","J",0],
    ["K","Q",0]
]

lj_range = [
    ["A","A", 2],["K","K", 2],["Q","Q", 2],["J","J", 2],["T","T", 2],["9","9", 2],["8","8", 2],["7","7", 2],["6","6",2],["5","5",2],
    ["A","K", 1],["A","Q", 1],["A","JK", 1],["A","T", 1],["A","9", 1],["A","8", 1],["A","7", 1],["A","6", 1],["A","5", 1],["A","4", 1],["A","3", 1],["A","3", 2],
    ["K","Q",1],["K","J",1],["K","T",1],["K","9",1],["K","8",1],["K","7",1],
    ["Q","J",1],["Q","T",1],
    ["J","T",1],
    ["T","9",1],
    ["A","K",0],["A","Q",0],["A","J",0],["A","T",0],
    ["K","Q",0],["K","J",0]
]
hj_range = [
    ["A","A", 2],["K","K", 2],["Q","Q", 2],["J","J", 2],["T","T", 2],["9","9", 2],["8","8", 2],["7","7", 2],["6","6",2],["5","5",2],
    ["A","K", 1],["A","Q", 1],["A","JK", 1],["A","T", 1],["A","9", 1],["A","8", 1],["A","7", 1],["A","6", 1],["A","5", 1],["A","4", 1],["A","3", 1],["A","3", 2],["A","2", 2],
    ["K","Q",1],["K","J",1],["K","T",1],["K","9",1],["K","8",1],["K","7",1],["K","6",1],["K","5",1],
    ["Q","J",1],["Q","T",1],["Q","9",1],
    ["J","T",1],["J","9",1],
    ["T","9",1],["T","8",1],
    ["A","K",0],["A","Q",0],["A","J",0],["A","T",0],
    ["K","Q",0],["K","J",0],["K","T",0],
    ["Q","J",0]
]
co_range = [
    ["A","A", 2],["K","K", 2],["Q","Q", 2],["J","J", 2],["T","T", 2],["9","9", 2],["8","8", 2],["7","7", 2],["6","6",2],["5","5",2],["4","4",2],
    ["A","K", 1],["A","Q", 1],["A","JK", 1],["A","T", 1],["A","9", 1],["A","8", 1],["A","7", 1],["A","6", 1],["A","5", 1],["A","4", 1],["A","3", 1],["A","3", 2],["A","2", 2],
    ["K","Q",1],["K","J",1],["K","T",1],["K","9",1],["K","8",1],["K","7",1],["K","6",1],["K","5",1],["K","4",1],
    ["Q","J",1],["Q","T",1],["Q","9",1],["Q","8",1],
    ["J","T",1],["J","9",1],["J","8",1],
    ["T","9",1],["T","8",1],
    ["9","8",1],["9","7",1],
    ["A","K",0],["A","Q",0],["A","J",0],["A","T",0],["A","9",0],
    ["K","Q",0],["K","J",0],["K","T",0],
    ["Q","J",0],["Q","T",0],
    ["J","T",0],
]
btn_range = [
    ["A","A", 2],["K","K", 2],["Q","Q", 2],["J","J", 2],["T","T", 2],["9","9", 2],["8","8", 2],["7","7", 2],["6","6",2],["5","5",2],["4","4",2],["3","3",2],["2","2",2],
    ["A","K", 1],["A","Q", 1],["A","JK", 1],["A","T", 1],["A","9", 1],["A","8", 1],["A","7", 1],["A","6", 1],["A","5", 1],["A","4", 1],["A","3", 1],["A","3", 2],["A","2", 2],
    ["K","Q",1],["K","J",1],["K","T",1],["K","9",1],["K","8",1],["K","7",1],["K","6",1],["K","5",1],["K","4",1],["K","3",1],["K","2",1],
    ["Q","J",1],["Q","T",1],["Q","9",1],["Q","8",1],["Q","7",1],["Q","6",1],["Q","5",1],["Q","4",1],["Q","3",1],
    ["J","T",1],["J","9",1],["J","8",1],["J","7",1],["J","6",1],["J","5",1],
    ["T","9",1],["T","8",1],["T","7",1],["T","6",1],
    ["9","8",1],["9","7",1],["9","6",1],
    ["8","6",1],
    ["7","6",1],["7","5",1],
    ["6","5",1],
    ["5","4",1],
    ["A","K",0],["A","Q",0],["A","J",0],["A","T",0],["A","9",0],["A","8",0],["A","7",0],["A","6",0],["A","5",0],["A","4",0],["A","3",0],
    ["K","Q",0],["K","J",0],["K","T",0],["K","9",0],
    ["Q","J",0],["Q","T",0],["Q","9",0],
    ["J","T",0],["J","9",0],
    ["T","9",0],
]
sb_range = [
    ["A","A", 2],["K","K", 2],["Q","Q", 2],["J","J", 2],["T","T", 2],["9","9", 2],["8","8", 2],["7","7", 2],["6","6",2],["5","5",2],["4","4",2],["3","3",2],["2","2",2],
    ["A","K", 1],["A","Q", 1],["A","JK", 1],["A","T", 1],["A","9", 1],["A","8", 1],["A","7", 1],["A","6", 1],["A","5", 1],["A","4", 1],["A","3", 1],["A","3", 2],["A","2", 2],
    ["K","Q",1],["K","J",1],["K","T",1],["K","9",1],["K","8",1],["K","7",1],["K","6",1],["K","5",1],["K","4",1],["K","3",1],["K","2",1],
    ["Q","J",1],["Q","T",1],["Q","9",1],["Q","8",1],["Q","7",1],["Q","6",1],["Q","5",1],["Q","4",1],["Q","3",1],
    ["J","T",1],["J","9",1],["J","8",1],["J","7",1],["J","6",1],["J","5",1],
    ["T","9",1],["T","8",1],["T","7",1],["T","6",1],
    ["9","8",1],["9","7",1],["9","6",1],
    ["8","6",1],
    ["7","6",1],["7","5",1],
    ["6","5",1],
    ["5","4",1],
    ["A","K",0],["A","Q",0],["A","J",0],["A","T",0],["A","9",0],["A","8",0],["A","7",0],["A","6",0],["A","5",0],["A","4",0],["A","3",0],
    ["K","Q",0],["K","J",0],["K","T",0],["K","9",0],
    ["Q","J",0],["Q","T",0],["Q","9",0],
    ["J","T",0],["J","9",0],
    ["T","9",0],
]


def build_range(my_range):
    formated_range = []
    for pair in my_range:
        formated_range.append(build_combonations([pair[0], pair[1]], pair[2]))
    formated_range = np.concatenate(formated_range).tolist()
    
    new_formated = []
    for i in range(len(formated_range)):
        if i%2 == 0:
            new_formated.append([formated_range[i], formated_range[i+1]])
    
    print(new_formated, "\n")
    return new_formated

utg_combos = build_range(utg_range)
lj_combos = build_range(lj_range)
hj_combos = build_range(hj_range)
co_combos = build_range(co_range)
btn_combos = build_range(btn_range)



"""utg_formated = []
for i in range(len(utg_combos)):
    if i%2 == 0:
        utg_formated.append([utg_combos[i], utg_combos[i+1]])

print(utg_formated)"""


"""from pypokerengine.api.emulator import Emulator
print(1/7)
# 1. Set game settings on emulator
emulator = Emulator()
emulator.set_game_rule(player_num=3, max_round=10, small_blind_amount=5, ante_amount=0)

# 2. Setup GameState object
players_info = {
    "uuid-1": { "name": "player1", "stack": 100 },
    "uuid-2": { "name": "player2", "stack": 100 },
    "uuid-3": { "name": "player3", "stack": 80 }
}
initial_state = emulator.generate_initial_game_state(players_info)
print("Initial State")
print(initial_state)
print("_________________________________________")
game_state, events = emulator.start_new_round(initial_state)
print("Game state")
print(game_state)
print("_________________________________________")
# 3. Run simulation and get updated GameState object
updated_state, events = emulator.apply_action(game_state, "raise", 15)
print("1",events[0]["round_state"])
print("2",updated_state)
print("3",events)

hole = updated_state["table"].seats.players[updated_state["next_player"]].hole_card
print(hole)

for card in hole:
    print(card)

while(events[0]['type'] != 'event_round_finish'):
    #if()
    updated_state, events = emulator.apply_action(updated_state, "call", 15)
    print("EVENTS: ", events)
    print("")
    print("Updated State: ", updated_state)
    print("")


'''
print("Updated State")
print(updated_state)
print("_________________________________________")
print("Events")
print(events)
print("_________________________________________")
print("Updated State")
print(updated_state)
print("_________________________________________")
updated_state, events = emulator.apply_action(updated_state, "fold", 10)
print("Updated State")
print(updated_state)
print("_________________________________________")
print("Events")
print(events)
print("_________________________________________")
print("Updated State")
print(updated_state)
print("_________________________________________")
updated_state, events = emulator.apply_action(updated_state, "call", 15)
print("_________________________________________")
print("Updated State")
print(events)
print("_________________________________________")
print("BOARD")
board = updated_state['table'].get_community_card()
for card in board:
    print(card.__str__())
print("_________________________________________")
print("Events")
print(events)
print("_________________________________________")
print("Updated State")
print(updated_state)
print("_________________________________________")
print(emulator.generate_possible_actions(updated_state))
print("_________________________________________")

print(events[0]["winners"])
print(len(events))
'''"""