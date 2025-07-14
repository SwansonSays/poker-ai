import numpy as np
from game_manager import GameManager

class ObsBuilder():
    def __init__(self):
        self.state = None
        

    def decode_action(self, action, possible_actions):
        return self.scale_bet(action, possible_actions[1]["amount"], possible_actions[-1]["amount"]["min"], possible_actions[-1]["amount"]["max"])

    # Take game state and build Observation
    def build_observation(self, game_state, events, total_chips, num_players):

        # 1. Encode active players Hole cards
        #       check that it is someones turn
        #       get active player
        #           get hole cards
        #           convert to hole cards obj to str
        #       encode hole cards str
        # 2. Encode board
        #       get board
        #           convert board obj to str
        #       fill empty spaces with CN
        #       encode board
        # 3. Encode current street
        #       get street
        #       encode street
        # 4. Encode the pot
        #       get pot
        #       encode pot
        # 5. Normalize each players chips and encode whether they are active in hand
        #       get all players
        #       get players uuid
        #       get players stack
        #       get total amount of chips
        #       get players status
        # 6. Encode active player
        #       check that it is someones turn
        #       get current player
        # 7. Encode previous actions (should i really encode every previous action taken every round or build the previous action arr for each round as it goes)
        #       get previous actions
        #       encode street
        #       encode player
        #       encode action
        #       encode bet
        # 8. Add all encodings to arr
        # 9. Return Observation

        #print("GET STATE")
        #print(game_state)

        """Encode Hole Cards"""
        #print("ERROR: ", game_state['next_player'])
        #print(game_state)
        #print(events[0]["type"])
        if(game_state["next_player"] != "not_found"):
            hole_cards_obj = game_state["table"].seats.players[game_state["next_player"]].hole_card
            #print(hole_cards_obj)
            hole_cards = []
            for card in hole_cards_obj:
                hole_cards.append(card.__str__())
        else:
            hole_cards = ["CN", "CN"]
        #print(hole_cards)
        
        normalized_hole_cards = self.normalize_cards(hole_cards)

        """Encode Community Cards"""
        board = []
        board_obj = game_state['table'].get_community_card()
        for card in board_obj:
            board.append(card.__str__())

        while len(board) < 5:
            board.append("CN")
        #print(board)

        normalized_board = self.normalize_cards(board)


        #print("BOARD: ",normalized_board)
        round_state = events[0]["round_state"]


        """Encode Street"""
        normalized_street = self.normalize_street(round_state["street"])


        """Normalize Pot"""
        normalized_pot = round_state["pot"]["main"]['amount'] / total_chips

        """Normalize Stacks / Encode Player Status"""
        player_status = [0] * num_players * 3
        i = 0
        for player in round_state["seats"]:
            player_status[i] = int(player["uuid"]) / num_players
            player_status[i + 1] = player["stack"] / total_chips
            if player['state'] == 'participating':
                player_status[i + 2] = 1
            else:
                player_status[i + 2] = 0
            i += 3

        """Encode Current Player"""
        if(game_state["next_player"] != "not_found"):
            current_player = round_state['next_player'] / num_players
        else:
            current_player = 0

        """Encode Previous Actions"""
        previous_actions = []

        for street in round_state["action_histories"]:
            for action in round_state["action_histories"][street]:
                #print(action)
                if(action["action"] == "FOLD"):
                    #print("IF")
                    full_action = [
                        self.normalize_street(street),
                        int(action["uuid"]) / num_players, 
                        self.normalize_action(action["action"]),
                        0
                    ]
                else:
                    #print("ELSE")
                    #print(action)
                    full_action = [
                        self.normalize_street(street),
                        int(action["uuid"]) / num_players, 
                        self.normalize_action(action["action"]),
                        self.normalize_bet(action["amount"], total_chips)
                    ]
                #print("160: ", full_action)

                previous_actions.append(np.array(full_action).flatten())

        while(len(previous_actions) < (50 * 4)):
            previous_actions.append(np.array([0,0,0,0]).flatten())
        """
        print("______________TEST____________")
        print(np.array(normalized_hole_cards).flatten())
        print(np.array(normalized_board).flatten())
        print(np.array(normalized_street))
        print(np.array(normalized_pot))
        print(np.array(player_status))
        print(np.array(current_player))
        print(np.array(previous_actions).flatten())
        """
        
        observation = np.concatenate([
            np.array(normalized_hole_cards).flatten(),
            np.array(normalized_board).flatten(),
            [normalized_street],
            [normalized_pot],
            np.array(player_status).flatten(),
            [current_player],
            np.array(previous_actions).flatten()
        ])
        """        
        print(state)
        print(len(state))
        """

        return observation
    
    def normalize_cards(self, cards):
        card_encoding = []
        card_mapping = {'C': 0, 'D': 1, 'H': 2, 'S': 3}  # Card suits: Clubs, Diamonds, Hearts, Spades
        rank_mapping = {'2': 0, '3': 1, '4': 2, '5': 3, '6': 4, '7': 5, '8': 6, '9': 7, 'T': 8, 'J': 9, 'Q': 10, 'K': 11, 'A': 12, 'N': 13} #"N" if no card

        for card in cards:
            suit = card[0]
            rank = card[1]
            suit_value = card_mapping[suit]
            rank_value = rank_mapping[rank]
            card_value = rank_value * 4 + suit_value
            card_encoding.append(card_value / 55)

        return card_encoding
    
    def normalize_street(self, street):
        if(street == "preflop"):
            street = 0
        elif(street == "flop"):
            street = 1
        elif(street == "turn"):
            street = 2
        elif(street == "river"):
            street = 3
        else:
            street = 4

        return street / 4
    
    def normalize_action(self, action):
        if(action == "SMALLBLIND"):
            action = 0
        elif(action == "BIGBLIND"):
            action = 1
        elif(action == "FOLD"):
            action = 2
        elif(action == "CALL"):
            action = 3
        elif(action == "RAISE"):
            action = 4

        return action / 4
    
    def normalize_bet(self, bet, total_chips):
        #print("NORMALIZE", bet)
        return bet / total_chips
    

    # Decode action and return
    def scale_bet(self, action, call_amount, min_bet, max_bet):
        #print(self.emulator.generate_possible_actions(self.game_state))
        #print(action, call_amount, min_bet, max_bet)
        if action <= 0.0:
            return "fold", 0
        elif action <0.5:
            return "call", call_amount
        elif action >= 0.5 and min_bet == -1:
            return "call", call_amount
        else:
            scaled_bet = min_bet + (max_bet - min_bet) * (action - 0.5) * 2
            #print("SCALE: ", float(min(max(scaled_bet, min_bet), max_bet )))
            return "raise", round(float(min(max(scaled_bet, min_bet), max_bet )), 1)