import numpy as np

class StateBuilder():
    def __init__(self):
        pass

    def _get_state(self, game_state, events):

        """Encode Hole Cards"""
        #print("ERROR: ", game_state['next_player'])
        #print(game_state)
        #print(events[0]["type"])
        if(game_state["next_player"] != "not_found"):
            hole_cards_obj = game_state["table"].seats.players[game_state["next_player"]].hole_card
            hole_cards = []
            for card in hole_cards_obj:
                hole_cards.append(card.__str__())
        else:
            hole_cards = ["CN", "CN"]
        
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
        normalized_pot = round_state["pot"]["main"]['amount'] / self.total_chips

        """Normalize Stacks / Encode Player Status"""
        player_status = [0] * self.num_players * 3
        i = 0
        for player in round_state["seats"]:
            player_status[i] = int(player["uuid"]) / self.num_players
            player_status[i + 1] = player["stack"] / self.total_chips
            if player['state'] == 'participating':
                player_status[i + 2] = 1
            else:
                player_status[i + 2] = 0
            i += 3

        """Encode Current Player"""
        if(game_state["next_player"] != "not_found"):
            current_player = round_state['next_player'] / self.num_players
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
                        int(action["uuid"]) / self.num_players, 
                        self.normalize_action(action["action"]),
                        0
                    ]
                else:
                    #print("ELSE")
                    #print(action)
                    full_action = [
                        self.normalize_street(street),
                        int(action["uuid"]) / self.num_players, 
                        self.normalize_action(action["action"]),
                        self.normalize_bet(action["amount"])
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
        
        state = np.concatenate([
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

        return state