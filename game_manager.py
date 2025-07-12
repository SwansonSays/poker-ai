from treys import Card, Deck, Evaluator

class GameManager():
    def __init__(self):
        pass

    def get_board(self):
        board = []
        board_obj = self.game_state['table'].get_community_card()

        for card in board_obj:
            board.append(card.__str__())
        return self.format_cards(board)        
        
    def format_cards(self, cards):
        new_cards = []
        for card in cards:
            card = card[0].lower() + card[1]
            new_cards.append(Card.new(card[::-1]))

        return new_cards
    
    def get_pretty(self, cards):
        return Card.ints_to_pretty_str(self.format_cards(cards))

    def get_cards(self):
        all_cards = []
        for player in self.game_state['table'].seats.players:
            hole_cards = []
            for card in player.hole_card:
                hole_cards.append(card.__str__())
            #print(player.name, self.get_pretty(hole_cards), player.stack)
            all_cards.append(self.format_cards(hole_cards))

        return all_cards
    
    def get_active_players_cards(self):
        all_cards = []
        for player in self.get_active_players():
            hole_cards = []
            if player.is_active(): #redudent?
                for card in player.hole_card:
                    hole_cards.append(card.__str__())
                #print(player.name, self.get_pretty(hole_cards), player.stack)
                all_cards.append(self.format_cards(hole_cards))

        return all_cards        
    
    def get_players_cards(self, player):
        if player != None:
            cards = []
            for card in player.hole_card:
                cards.append(card.__str__())
            return self.format_cards(cards)
        else:
            return None

    def get_street(self):
        if self.game_state["street"] == 0:
            return "PREFLOP"        
        elif self.game_state["street"] == 1:
            return "FLOP"
        elif self.game_state["street"] == 2:
            return "TURN"
        elif self.game_state["street"] == 3:
            return "RIVER"
        elif self.game_state["street"] == 4:
            return "SHOWDOWN"
        elif self.game_state["street"] == 5:
            return "FINISHED"

    def get_player(self, uuid):
        return self.game_state['table'].seats.players[uuid - 1]

    def get_active_players(self):
        active_players = []
        for player in self.game_state['table'].seats.players:
            if player.is_active():
                active_players.append(player)
                
        return active_players
    
    def get_table(self):
        return self.game_state['table']
        
    def get_current_player(self):
        if self.game_state["next_player"] != "not_found":
            return self.get_player(self.game_state["next_player"])
        else:
            return None