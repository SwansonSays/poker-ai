class ObsBuilder():
    def __init__(self):
        pass

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
    
    def normalize_bet(self, bet):
        #print("NORMALIZE", bet)
        return bet / self.total_chips
    
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