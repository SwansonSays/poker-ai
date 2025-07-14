from pypokerengine.players import BasePokerPlayer
from pypokerengine.api.emulator import Emulator
import pypokerengine.engine.action_checker as Action

from treys import Card, Deck, Evaluator

class GameManager():
    def __init__(self, num_players):
        self.num_players = num_players
        self.players = [BasePokerPlayer() for _ in range(self.num_players)]  # Placeholder players

        self.emulator = None
        self.game_state = None
        self.events = None
        self.buy_in = 100
        self.total_chips = self.buy_in * self.num_players


    # Create new game and return initial game state
    def create_game(self):
        print("         * * * * * * * *")
        print("         *  NEW GAME!  *")
        print("         * * * * * * * *","\n")

        self.emulator = Emulator()
        self.emulator.set_game_rule(player_num=self.num_players, max_round=10, small_blind_amount=5, ante_amount=0)
        players_info = {
            "1": { "name": "player1", "stack": self.buy_in },
            "2": { "name": "player2", "stack": self.buy_in },
            "3": { "name": "player3", "stack": self.buy_in },
            "4": { "name": "player4", "stack": self.buy_in },
            "5": { "name": "player5", "stack": self.buy_in },
            "6": { "name": "player6", "stack": self.buy_in },
            "7": { "name": "player7", "stack": self.buy_in }
        }

        initial_state = self.emulator.generate_initial_game_state(players_info)
        self.game_state, self.events = self.emulator.start_new_round(initial_state)

        return self.game_state, self.events
    
    # Check Winners
    def check_winners(self):
        for event in self.events:
            if "winners" in event:
                return True            
            else: 
                return False
            
    # Generate possible actions for current game state
    def get_possible_actions(self):
        return self.emulator.generate_possible_actions(self.game_state)
    
    # Take decoded action and update game state
    def take_action(self, action_name, amount):
        self.game_state, self.events = self.emulator.apply_action(self.game_state, action_name, amount)
        return self.game_state, self.events

    #Returns board as string from game_state
    def get_board(self):
        board = []
        board_obj = self.game_state['table'].get_community_card()

        for card in board_obj:
            board.append(card.__str__())
        return self.format_cards(board)     
        
    #Reverses cards from game engine notation and creates treys card object
    def format_cards(self, cards):
        new_cards = []
        for card in cards:
            card = card[0].lower() + card[1]
            new_cards.append(Card.new(card[::-1]))

        return new_cards
    
    #Takes game engine cards, creates treys object, returns pretty string
    def get_pretty(self, cards):
        return Card.ints_to_pretty_str(self.format_cards(cards))

    #Returns array of all players cards as trey object
    def get_cards(self):
        all_cards = []
        for player in self.game_state['table'].seats.players:
            hole_cards = []
            for card in player.hole_card:
                hole_cards.append(card.__str__())
            #print(player.name, self.get_pretty(hole_cards), player.stack)
            all_cards.append(self.format_cards(hole_cards))

        return all_cards
    
    #returns array of all players still active in hand cards as trey object
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
    
    #Takes player object and returns cards as trey object
    def get_players_cards(self, player):
        if player != None:
            cards = []
            for card in player.hole_card:
                cards.append(card.__str__())
            return self.format_cards(cards)
        else:
            return None

    #Takes game_state street number and returns string
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

    #returns player object from uuid. Doesnt chekc for vaild uuid
    def get_player(self, uuid):
        return self.game_state['table'].seats.players[uuid - 1]

    #returns array of active player objects currently in hand
    def get_active_players(self):
        active_players = []
        for player in self.game_state['table'].seats.players:
            if player.is_active():
                active_players.append(player)
                
        return active_players
    
    #returns table object from game_state
    def get_table(self):
        return self.game_state['table']
        
    #Returns active player from game_state
    def get_current_player(self):
        if self.game_state["next_player"] != "not_found":
            return self.get_player(self.game_state["next_player"])
        else:
            return None
        
    #returns total chips on table
    def get_total_chips(self):
        return self.total_chips