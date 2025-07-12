from stable_baselines3 import PPO
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from pypokerengine.players import BasePokerPlayer
from pypokerengine.api.emulator import Emulator
import pypokerengine.engine.action_checker as Action
import random
from treys import Card, Deck, Evaluator

class PokerGymEnv(gym.Env):
    def __init__(self, num_players=7):
        super(PokerGymEnv, self).__init__()
        hand = [Card.new('Ah'), Card.new('Kd')]
        hand1 = [Card.new('Kd'), Card.new('Ah')]
        print(hand, hand1)

        # Define action space (fold, call, raise)
        self.action_space = spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)

        # Define observation space (agent's hand, community cards, stack sizes)
        self.observation_space = spaces.Box(low=0, high=1, shape=(831,), dtype=np.float32)

        # Set up the number of players
        self.num_players = num_players
        self.players = [BasePokerPlayer() for _ in range(self.num_players)]  # Placeholder players
        self.state = None
        self.emulator = None
        self.game_state = None
        self.events = None
        self.buy_in = 100
        self.total_chips = self.buy_in * self.num_players
        self.render_mode = "human"

    def reset(self, seed=None):
        print("         * * * * * * * *")
        print("         *  NEW GAME!  *")
        print("         * * * * * * * *","\n")

        self.emulator = Emulator()
        self.emulator.set_game_rule(player_num=7, max_round=10, small_blind_amount=5, ante_amount=0)
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

        #print(self.game_state['table']._blind_pos)
        #print(self.game_state['table'].dealer_btn)



        self.state = self._get_state(self.game_state, self.events)

        if self.render_mode == "human":
            self.render()

        return self.state, {}

    def step(self, action):
        
        #print(self.events[0]["type"])
        #Reset on hand win
        for event in self.events:
            if "winners" in event:
                done = True
                #print(event["winners"][0]["stack"])
                self.reset()             
            else: 
                done = False
                
        #transalte action based on possible actions
        possible_actions = self.emulator.generate_possible_actions(self.game_state)
        print(possible_actions)
        action_name, amount = self.scale_bet(action, possible_actions[1]["amount"], possible_actions[-1]["amount"]["min"], possible_actions[-1]["amount"]["max"])
        print(action_name, amount)
        #print("Player: ", self.game_state["next_player"], action_name, amount)
        #print("POT: ", self.events[0]["round_state"]["pot"]["main"]['amount'])

        reward = self.calculate_reward(action_name)

        #take action
        self.game_state, self.events = self.emulator.apply_action(self.game_state, action_name, amount)

        # Check if the game is over
        #I think this is redundent now
        if (self.events[0]['type'] == 'event_round_finish'):
            done = True
        else:
            done = False

        # Get the updated state
        self.state = self._get_state(self.game_state, self.events)

        #print(f"Reward: {reward}")

        if self.render_mode == "human":
            self.render(action_name, amount, reward)

        return self.state, reward, done, False, {}

    def render(self, action='none', amount='none', reward='none', mode='human'):
        if(self.events[0]["type"] == "event_new_street"):
            print("*******************************************")
            
            if(self.get_street() == "PREFLOP" or self.get_street() == "FINISHED"):
                print("         ", self.get_street())
            elif(self.get_street() != "PREFLOP" or self.get_street() != "FINISHED"):
                print(self.get_street(), end=":")
                Card.print_pretty_cards(self.get_board())

            print("*******************************************")

        for player in self.get_active_players():
            #print(player.name, Card.ints_to_pretty_str(self.get_players_cards(player)), "Stack:", player.stack)
            pass


        

        if(self.get_street() != "FINISHED"):
            if(action == "call"):
                print(f"Player {self.game_state["next_player"]} {action}s {amount} with{Card.ints_to_pretty_str(self.get_players_cards(self.get_current_player()))}({reward})")
            elif(action == "raise"):
                print(f"Player {self.game_state["next_player"]} {action}s to {amount} with{Card.ints_to_pretty_str(self.get_players_cards(self.get_current_player()))}({reward})")
            elif(action == 'fold'):
                print(f"Player {self.game_state["next_player"]} {action}s {Card.ints_to_pretty_str(self.get_players_cards(self.get_current_player()))}({reward})")

        else:
            #print("WINNER WINNER")
            for event in self.events:
                #print(event)
                #print("*****")
                #print(self.events[-1]["community_cards"])
                if "winners" in event:
                    winner = self.get_player(int(event["winners"][0]['uuid']))
                    print("         * * * * * * * * *")
                    print("         * Player", winner.uuid, "WINS *")
                    print("         * * * * * * * * *")
                    print("Player",event["winners"][0]['uuid'], 
                          "wins ", event["round_state"]["pot"]["main"]["amount"],
                          "with", Card.ints_to_pretty_str(self.get_players_cards(winner)), 
                          "on board", Card.ints_to_pretty_str(self.get_board()), "\n")

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

    def calculate_reward(self, action):
        self.get_street()
        if(self.game_state["next_player"] != "not_found"): # != to new game/ new street event
            hole_cards = self.get_players_cards(self.get_player(self.game_state["next_player"]))
        else:
            return 0
        
        

        if(self.get_street() == "PREFLOP"):
            return self.preflop_rfi(self.get_player(self.game_state["next_player"]), action)
        
        return self.monte_carlo_sim(hole_cards, self.get_board())
    
    def monte_carlo_sim(self, hand, board, simulations=5000):
        evaluator = Evaluator()
        deck = Deck()
        self.get_active_players()
        num_active_players = self.game_state['table'].seats.count_active_players()

        wins = 0
        known_cards = []
        known_cards += board

        for cards in self.get_cards():
            known_cards += cards 

        #print(Card.print_pretty_cards(known_cards))

        wins_by_player = [0] * self.num_players
        i = 0
        while i < num_active_players * 2:
            if(hand[0] != known_cards[i + len(board)]):
                for _ in range(int(simulations/(num_active_players - 1))):
                    deck.shuffle()
                    for card in known_cards:
                        deck.cards.remove(card)

                    opponent_hand = [known_cards[i + len(board)], known_cards[i + len(board) + 1]]
                    full_board = board + deck.draw(5 - len(board))

                    #print(Card.print_pretty_cards(hand), Card.print_pretty_cards(opponent_hand))
                    hero_score = evaluator.evaluate(hand, full_board)
                    villian_score = evaluator.evaluate(opponent_hand, full_board)

                    if hero_score < villian_score:
                        wins += 1
                        wins_by_player[int(i/2)] += 1
            i += 2

        for i in range(len(wins_by_player)):
            wins_by_player[i] = round(wins_by_player[i] / simulations * 100, 2)

        #print(wins_by_player)
        #print("WINS:", wins)

        
        #return wins/simulations
        return wins/simulations
    
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

    def preflop_rfi(self, player, action):
        cards = self.get_players_cards(player)
        print("!!")
        print(vars(player))

        #UTG is player 3 so we start there
        if(player.uuid == '3'):
            range = [['Ah', 'Ad'], ['Ah', 'Ac'], ['Ah', 'As'], ['Ad', 'Ac'], ['Ad', 'As'], ['Ac', 'As'], 
                    ['Kh', 'Kd'], ['Kh', 'Kc'], ['Kh', 'Ks'], ['Kd', 'Kc'], ['Kd', 'Ks'], ['Kc', 'Ks'], 
                    ['Qh', 'Qd'], ['Qh', 'Qc'], ['Qh', 'Qs'], ['Qd', 'Qc'], ['Qd', 'Qs'], ['Qc', 'Qs'], 
                    ['Jh', 'Jd'], ['Jh', 'Jc'], ['Jh', 'Js'], ['Jd', 'Jc'], ['Jd', 'Js'], ['Jc', 'Js'], 
                    ['Th', 'Td'], ['Th', 'Tc'], ['Th', 'Ts'], ['Td', 'Tc'], ['Td', 'Ts'], ['Tc', 'Ts'], 
                    ['9h', '9d'], ['9h', '9c'], ['9h', '9s'], ['9d', '9c'], ['9d', '9s'], ['9c', '9s'], 
                    ['8h', '8d'], ['8h', '8c'], ['8h', '8s'], ['8d', '8c'], ['8d', '8s'], ['8c', '8s'], 
                    ['7h', '7d'], ['7h', '7c'], ['7h', '7s'], ['7d', '7c'], ['7d', '7s'], ['7c', '7s'], 
                    ['Ah', 'Kh'], ['Ad', 'Kd'], ['Ac', 'Kc'], ['As', 'Ks'], ['Ah', 'Qh'], ['Ad', 'Qd'], ['Ac', 'Qc'], ['As', 'Qs'], ['Ah', 'JKh'], ['Ad', 'JKd'], ['Ac', 'JKc'], ['As', 'JKs'], ['Ah', 'Th'], ['Ad', 'Td'], ['Ac', 'Tc'], ['As', 'Ts'], ['Ah', '9h'], ['Ad', '9d'], ['Ac', '9c'], ['As', '9s'], ['Ah', '8h'], ['Ad', '8d'], ['Ac', '8c'], ['As', '8s'], ['Ah', '7h'], ['Ad', '7d'], ['Ac', '7c'], ['As', '7s'], ['Ah', '6h'], ['Ad', '6d'], ['Ac', '6c'], ['As', '6s'], ['Ah', '5h'], ['Ad', '5d'], ['Ac', '5c'], ['As', '5s'], ['Ah', '4h'], ['Ad', '4d'], ['Ac', '4c'], ['As', '4s'], ['Ah', '3h'], ['Ad', '3d'], ['Ac', '3c'], ['As', '3s'], 
                    ['Kh', 'Qh'], ['Kd', 'Qd'], ['Kc', 'Qc'], ['Ks', 'Qs'], ['Kh', 'Jh'], ['Kd', 'Jd'], ['Kc', 'Jc'], ['Ks', 'Js'], ['Kh', 'Th'], ['Kd', 'Td'], ['Kc', 'Tc'], ['Ks', 'Ts'], ['Kh', '9h'], ['Kd', '9d'], ['Kc', '9c'], ['Ks', '9s'], 
                    ['Qh', 'Jh'], ['Qd', 'Jd'], ['Qc', 'Jc'], ['Qs', 'Js'], ['Qh', 'Th'], ['Qd', 'Td'], ['Qc', 'Tc'], ['Qs', 'Ts'], 
                    ['Jh', 'Th'], ['Jd', 'Td'], ['Jc', 'Tc'], ['Js', 'Ts'], 
                    ['Th', '9h'], ['Td', '9d'], ['Tc', '9c'], ['Ts', '9s'], 
                    ['Ah', 'Kd'], ['Ah', 'Kc'], ['Ah', 'Ks'], ['Ad', 'Ks'], ['Ac', 'Kd'], ['Ac', 'Kh'], ['Ac', 'Ks'], ['As', 'Kd'], ['As', 'Kc'], ['As', 'Kh'], ['Ah', 'Qd'], ['Ah', 'Qc'], ['Ah', 'Qs'], ['Ad', 'Qs'], ['Ac', 'Qd'], ['Ac', 'Qh'], ['Ac', 'Qs'], ['As', 'Qd'], ['As', 'Qc'], ['As', 'Qh'], ['Ah', 'Jd'], ['Ah', 'Jc'], ['Ah', 'Js'], ['Ad', 'Js'], ['Ac', 'Jd'], ['Ac', 'Jh'], ['Ac', 'Js'], ['As', 'Jd'], ['As', 'Jc'], ['As', 'Jh'], 
                    ['Kh', 'Qd'], ['Kh', 'Qc'], ['Kh', 'Qs'], ['Kd', 'Qs'], ['Kc', 'Qd'], ['Kc', 'Qh'], ['Kc', 'Qs'], ['Ks', 'Qd'], ['Ks', 'Qc'], ['Ks', 'Qh']] 
            return self.compare_hand_with_range(cards, range, action)
        elif(player.uuid == '4'):
            range = [['Ah', 'Ad'], ['Ah', 'Ac'], ['Ah', 'As'], ['Ad', 'Ac'], ['Ad', 'As'], ['Ac', 'As'], 
                    ['Kh', 'Kd'], ['Kh', 'Kc'], ['Kh', 'Ks'], ['Kd', 'Kc'], ['Kd', 'Ks'], ['Kc', 'Ks'], 
                    ['Qh', 'Qd'], ['Qh', 'Qc'], ['Qh', 'Qs'], ['Qd', 'Qc'], ['Qd', 'Qs'], ['Qc', 'Qs'], 
                    ['Jh', 'Jd'], ['Jh', 'Jc'], ['Jh', 'Js'], ['Jd', 'Jc'], ['Jd', 'Js'], ['Jc', 'Js'], 
                    ['Th', 'Td'], ['Th', 'Tc'], ['Th', 'Ts'], ['Td', 'Tc'], ['Td', 'Ts'], ['Tc', 'Ts'], 
                    ['9h', '9d'], ['9h', '9c'], ['9h', '9s'], ['9d', '9c'], ['9d', '9s'], ['9c', '9s'], 
                    ['8h', '8d'], ['8h', '8c'], ['8h', '8s'], ['8d', '8c'], ['8d', '8s'], ['8c', '8s'], 
                    ['7h', '7d'], ['7h', '7c'], ['7h', '7s'], ['7d', '7c'], ['7d', '7s'], ['7c', '7s'], 
                    ['6h', '6d'], ['6h', '6c'], ['6h', '6s'], ['6d', '6c'], ['6d', '6s'], ['6c', '6s'], 
                    ['5h', '5d'], ['5h', '5c'], ['5h', '5s'], ['5d', '5c'], ['5d', '5s'], ['5c', '5s'], 
                    ['Ah', 'Kh'], ['Ad', 'Kd'], ['Ac', 'Kc'], ['As', 'Ks'], ['Ah', 'Qh'], ['Ad', 'Qd'], ['Ac', 'Qc'], ['As', 'Qs'], ['Ah', 'JKh'], ['Ad', 'JKd'], ['Ac', 'JKc'], ['As', 'JKs'], ['Ah', 'Th'], ['Ad', 'Td'], ['Ac', 'Tc'], ['As', 'Ts'], ['Ah', '9h'], ['Ad', '9d'], ['Ac', '9c'], ['As', '9s'], ['Ah', '8h'], ['Ad', '8d'], ['Ac', '8c'], ['As', '8s'], ['Ah', '7h'], ['Ad', '7d'], ['Ac', '7c'], ['As', '7s'], ['Ah', '6h'], ['Ad', '6d'], ['Ac', '6c'], ['As', '6s'], ['Ah', '5h'], ['Ad', '5d'], ['Ac', '5c'], ['As', '5s'], ['Ah', '4h'], ['Ad', '4d'], ['Ac', '4c'], ['As', '4s'], ['Ah', '3h'], ['Ad', '3d'], ['Ac', '3c'], ['As', '3s'], ['Ah', '3d'], ['Ah', '3c'], ['Ah', '3s'], ['Ad', '3c'], ['Ad', '3s'], ['Ac', '3s'], 
                    ['Kh', 'Qh'], ['Kd', 'Qd'], ['Kc', 'Qc'], ['Ks', 'Qs'], ['Kh', 'Jh'], ['Kd', 'Jd'], ['Kc', 'Jc'], ['Ks', 'Js'], ['Kh', 'Th'], ['Kd', 'Td'], ['Kc', 'Tc'], ['Ks', 'Ts'], ['Kh', '9h'], ['Kd', '9d'], ['Kc', '9c'], ['Ks', '9s'], ['Kh', '8h'], ['Kd', '8d'], ['Kc', '8c'], ['Ks', '8s'], ['Kh', '7h'], ['Kd', '7d'], ['Kc', '7c'], ['Ks', '7s'], 
                    ['Qh', 'Jh'], ['Qd', 'Jd'], ['Qc', 'Jc'], ['Qs', 'Js'], ['Qh', 'Th'], ['Qd', 'Td'], ['Qc', 'Tc'], ['Qs', 'Ts'], 
                    ['Jh', 'Th'], ['Jd', 'Td'], ['Jc', 'Tc'], ['Js', 'Ts'], 
                    ['Th', '9h'], ['Td', '9d'], ['Tc', '9c'], ['Ts', '9s'], 
                    ['Ah', 'Kd'], ['Ah', 'Kc'], ['Ah', 'Ks'], ['Ad', 'Ks'], ['Ac', 'Kd'], ['Ac', 'Kh'], ['Ac', 'Ks'], ['As', 'Kd'], ['As', 'Kc'], ['As', 'Kh'], ['Ah', 'Qd'], ['Ah', 'Qc'], ['Ah', 'Qs'], ['Ad', 'Qs'], ['Ac', 'Qd'], ['Ac', 'Qh'], ['Ac', 'Qs'], ['As', 'Qd'], ['As', 'Qc'], ['As', 'Qh'], ['Ah', 'Jd'], ['Ah', 'Jc'], ['Ah', 'Js'], ['Ad', 'Js'], ['Ac', 'Jd'], ['Ac', 'Jh'], ['Ac', 'Js'], ['As', 'Jd'], ['As', 'Jc'], ['As', 'Jh'], ['Ah', 'Td'], ['Ah', 'Tc'], ['Ah', 'Ts'], ['Ad', 'Ts'], ['Ac', 'Td'], ['Ac', 'Th'], ['Ac', 'Ts'], ['As', 'Td'], ['As', 'Tc'], ['As', 'Th'], 
                    ['Kh', 'Qd'], ['Kh', 'Qc'], ['Kh', 'Qs'], ['Kd', 'Qs'], ['Kc', 'Qd'], ['Kc', 'Qh'], ['Kc', 'Qs'], ['Ks', 'Qd'], ['Ks', 'Qc'], ['Ks', 'Qh'], ['Kh', 'Jd'], ['Kh', 'Jc'], ['Kh', 'Js'], ['Kd', 'Js'], ['Kc', 'Jd'], ['Kc', 'Jh'], ['Kc', 'Js'], ['Ks', 'Jd'], ['Ks', 'Jc'], ['Ks', 'Jh']] 
            return self.compare_hand_with_range(cards, range, action)
        elif(player.uuid == '5'):
            range = [['Ah', 'Ad'], ['Ah', 'Ac'], ['Ah', 'As'], ['Ad', 'Ac'], ['Ad', 'As'], ['Ac', 'As'], 
                    ['Kh', 'Kd'], ['Kh', 'Kc'], ['Kh', 'Ks'], ['Kd', 'Kc'], ['Kd', 'Ks'], ['Kc', 'Ks'], 
                    ['Qh', 'Qd'], ['Qh', 'Qc'], ['Qh', 'Qs'], ['Qd', 'Qc'], ['Qd', 'Qs'], ['Qc', 'Qs'], 
                    ['Jh', 'Jd'], ['Jh', 'Jc'], ['Jh', 'Js'], ['Jd', 'Jc'], ['Jd', 'Js'], ['Jc', 'Js'], 
                    ['Th', 'Td'], ['Th', 'Tc'], ['Th', 'Ts'], ['Td', 'Tc'], ['Td', 'Ts'], ['Tc', 'Ts'], 
                    ['9h', '9d'], ['9h', '9c'], ['9h', '9s'], ['9d', '9c'], ['9d', '9s'], ['9c', '9s'], 
                    ['8h', '8d'], ['8h', '8c'], ['8h', '8s'], ['8d', '8c'], ['8d', '8s'], ['8c', '8s'], 
                    ['7h', '7d'], ['7h', '7c'], ['7h', '7s'], ['7d', '7c'], ['7d', '7s'], ['7c', '7s'], 
                    ['6h', '6d'], ['6h', '6c'], ['6h', '6s'], ['6d', '6c'], ['6d', '6s'], ['6c', '6s'], 
                    ['5h', '5d'], ['5h', '5c'], ['5h', '5s'], ['5d', '5c'], ['5d', '5s'], ['5c', '5s'], 
                    ['Ah', 'Kh'], ['Ad', 'Kd'], ['Ac', 'Kc'], ['As', 'Ks'], ['Ah', 'Qh'], ['Ad', 'Qd'], ['Ac', 'Qc'], ['As', 'Qs'], ['Ah', 'JKh'], ['Ad', 'JKd'], ['Ac', 'JKc'], ['As', 'JKs'], ['Ah', 'Th'], ['Ad', 'Td'], ['Ac', 'Tc'], ['As', 'Ts'], ['Ah', '9h'], ['Ad', '9d'], ['Ac', '9c'], ['As', '9s'], ['Ah', '8h'], ['Ad', '8d'], ['Ac', '8c'], ['As', '8s'], ['Ah', '7h'], ['Ad', '7d'], ['Ac', '7c'], ['As', '7s'], ['Ah', '6h'], ['Ad', '6d'], ['Ac', '6c'], ['As', '6s'], ['Ah', '5h'], ['Ad', '5d'], ['Ac', '5c'], ['As', '5s'], ['Ah', '4h'], ['Ad', '4d'], ['Ac', '4c'], ['As', '4s'], ['Ah', '3h'], ['Ad', '3d'], ['Ac', '3c'], ['As', '3s'], ['Ah', '3d'], ['Ah', '3c'], ['Ah', '3s'], ['Ad', '3c'], ['Ad', '3s'], ['Ac', '3s'], ['Ah', '2d'], ['Ah', '2c'], ['Ah', '2s'], ['Ad', '2c'], ['Ad', '2s'], ['Ac', '2s'], 
                    ['Kh', 'Qh'], ['Kd', 'Qd'], ['Kc', 'Qc'], ['Ks', 'Qs'], ['Kh', 'Jh'], ['Kd', 'Jd'], ['Kc', 'Jc'], ['Ks', 'Js'], ['Kh', 'Th'], ['Kd', 'Td'], ['Kc', 'Tc'], ['Ks', 'Ts'], ['Kh', '9h'], ['Kd', '9d'], ['Kc', '9c'], ['Ks', '9s'], ['Kh', '8h'], ['Kd', '8d'], ['Kc', '8c'], ['Ks', '8s'], ['Kh', '7h'], ['Kd', '7d'], ['Kc', '7c'], ['Ks', '7s'], ['Kh', '6h'], ['Kd', '6d'], ['Kc', '6c'], ['Ks', '6s'], ['Kh', '5h'], ['Kd', '5d'], ['Kc', '5c'], ['Ks', '5s'], 
                    ['Qh', 'Jh'], ['Qd', 'Jd'], ['Qc', 'Jc'], ['Qs', 'Js'], ['Qh', 'Th'], ['Qd', 'Td'], ['Qc', 'Tc'], ['Qs', 'Ts'], ['Qh', '9h'], ['Qd', '9d'], ['Qc', '9c'], ['Qs', '9s'], 
                    ['Jh', 'Th'], ['Jd', 'Td'], ['Jc', 'Tc'], ['Js', 'Ts'], ['Jh', '9h'], ['Jd', '9d'], ['Jc', '9c'], ['Js', '9s'], 
                    ['Th', '9h'], ['Td', '9d'], ['Tc', '9c'], ['Ts', '9s'], ['Th', '8h'], ['Td', '8d'], ['Tc', '8c'], ['Ts', '8s'], 
                    ['Ah', 'Kd'], ['Ah', 'Kc'], ['Ah', 'Ks'], ['Ad', 'Ks'], ['Ac', 'Kd'], ['Ac', 'Kh'], ['Ac', 'Ks'], ['As', 'Kd'], ['As', 'Kc'], ['As', 'Kh'], ['Ah', 'Qd'], ['Ah', 'Qc'], ['Ah', 'Qs'], ['Ad', 'Qs'], ['Ac', 'Qd'], ['Ac', 'Qh'], ['Ac', 'Qs'], ['As', 'Qd'], ['As', 'Qc'], ['As', 'Qh'], ['Ah', 'Jd'], ['Ah', 'Jc'], ['Ah', 'Js'], ['Ad', 'Js'], ['Ac', 'Jd'], ['Ac', 'Jh'], ['Ac', 'Js'], ['As', 'Jd'], ['As', 'Jc'], ['As', 'Jh'], ['Ah', 'Td'], ['Ah', 'Tc'], ['Ah', 'Ts'], ['Ad', 'Ts'], ['Ac', 'Td'], ['Ac', 'Th'], ['Ac', 'Ts'], ['As', 'Td'], ['As', 'Tc'], ['As', 'Th'], 
                    ['Kh', 'Qd'], ['Kh', 'Qc'], ['Kh', 'Qs'], ['Kd', 'Qs'], ['Kc', 'Qd'], ['Kc', 'Qh'], ['Kc', 'Qs'], ['Ks', 'Qd'], ['Ks', 'Qc'], ['Ks', 'Qh'], ['Kh', 'Jd'], ['Kh', 'Jc'], ['Kh', 'Js'], ['Kd', 'Js'], ['Kc', 'Jd'], ['Kc', 'Jh'], ['Kc', 'Js'], ['Ks', 'Jd'], ['Ks', 'Jc'], ['Ks', 'Jh'], ['Kh', 'Td'], ['Kh', 'Tc'], ['Kh', 'Ts'], ['Kd', 'Ts'], ['Kc', 'Td'], ['Kc', 'Th'], ['Kc', 'Ts'], ['Ks', 'Td'], ['Ks', 'Tc'], ['Ks', 'Th'], 
                    ['Qh', 'Jd'], ['Qh', 'Jc'], ['Qh', 'Js'], ['Qd', 'Js'], ['Qc', 'Jd'], ['Qc', 'Jh'], ['Qc', 'Js'], ['Qs', 'Jd'], ['Qs', 'Jc'], ['Qs', 'Jh']]
            return self.compare_hand_with_range(cards, range, action)
        elif(player.uuid == '6'):
            range = [['Ah', 'Ad'], ['Ah', 'Ac'], ['Ah', 'As'], ['Ad', 'Ac'], ['Ad', 'As'], ['Ac', 'As'], 
                    ['Kh', 'Kd'], ['Kh', 'Kc'], ['Kh', 'Ks'], ['Kd', 'Kc'], ['Kd', 'Ks'], ['Kc', 'Ks'], 
                    ['Qh', 'Qd'], ['Qh', 'Qc'], ['Qh', 'Qs'], ['Qd', 'Qc'], ['Qd', 'Qs'], ['Qc', 'Qs'], 
                    ['Jh', 'Jd'], ['Jh', 'Jc'], ['Jh', 'Js'], ['Jd', 'Jc'], ['Jd', 'Js'], ['Jc', 'Js'], 
                    ['Th', 'Td'], ['Th', 'Tc'], ['Th', 'Ts'], ['Td', 'Tc'], ['Td', 'Ts'], ['Tc', 'Ts'], 
                    ['9h', '9d'], ['9h', '9c'], ['9h', '9s'], ['9d', '9c'], ['9d', '9s'], ['9c', '9s'], 
                    ['8h', '8d'], ['8h', '8c'], ['8h', '8s'], ['8d', '8c'], ['8d', '8s'], ['8c', '8s'], 
                    ['7h', '7d'], ['7h', '7c'], ['7h', '7s'], ['7d', '7c'], ['7d', '7s'], ['7c', '7s'], 
                    ['6h', '6d'], ['6h', '6c'], ['6h', '6s'], ['6d', '6c'], ['6d', '6s'], ['6c', '6s'], 
                    ['5h', '5d'], ['5h', '5c'], ['5h', '5s'], ['5d', '5c'], ['5d', '5s'], ['5c', '5s'], 
                    ['4h', '4d'], ['4h', '4c'], ['4h', '4s'], ['4d', '4c'], ['4d', '4s'], ['4c', '4s'], 
                    ['Ah', 'Kh'], ['Ad', 'Kd'], ['Ac', 'Kc'], ['As', 'Ks'], ['Ah', 'Qh'], ['Ad', 'Qd'], ['Ac', 'Qc'], ['As', 'Qs'], ['Ah', 'JKh'], ['Ad', 'JKd'], ['Ac', 'JKc'], ['As', 'JKs'], ['Ah', 'Th'], ['Ad', 'Td'], ['Ac', 'Tc'], ['As', 'Ts'], ['Ah', '9h'], ['Ad', '9d'], ['Ac', '9c'], ['As', '9s'], ['Ah', '8h'], ['Ad', '8d'], ['Ac', '8c'], ['As', '8s'], ['Ah', '7h'], ['Ad', '7d'], ['Ac', '7c'], ['As', '7s'], ['Ah', '6h'], ['Ad', '6d'], ['Ac', '6c'], ['As', '6s'], ['Ah', '5h'], ['Ad', '5d'], ['Ac', '5c'], ['As', '5s'], ['Ah', '4h'], ['Ad', '4d'], ['Ac', '4c'], ['As', '4s'], ['Ah', '3h'], ['Ad', '3d'], ['Ac', '3c'], ['As', '3s'], ['Ah', '3d'], ['Ah', '3c'], ['Ah', '3s'], ['Ad', '3c'], ['Ad', '3s'], ['Ac', '3s'], ['Ah', '2d'], ['Ah', '2c'], ['Ah', '2s'], ['Ad', '2c'], ['Ad', '2s'], ['Ac', '2s'], 
                    ['Kh', 'Qh'], ['Kd', 'Qd'], ['Kc', 'Qc'], ['Ks', 'Qs'], ['Kh', 'Jh'], ['Kd', 'Jd'], ['Kc', 'Jc'], ['Ks', 'Js'], ['Kh', 'Th'], ['Kd', 'Td'], ['Kc', 'Tc'], ['Ks', 'Ts'], ['Kh', '9h'], ['Kd', '9d'], ['Kc', '9c'], ['Ks', '9s'], ['Kh', '8h'], ['Kd', '8d'], ['Kc', '8c'], ['Ks', '8s'], ['Kh', '7h'], ['Kd', '7d'], ['Kc', '7c'], ['Ks', '7s'], ['Kh', '6h'], ['Kd', '6d'], ['Kc', '6c'], ['Ks', '6s'], ['Kh', '5h'], ['Kd', '5d'], ['Kc', '5c'], ['Ks', '5s'], ['Kh', '4h'], ['Kd', '4d'], ['Kc', '4c'], ['Ks', '4s'], 
                    ['Qh', 'Jh'], ['Qd', 'Jd'], ['Qc', 'Jc'], ['Qs', 'Js'], ['Qh', 'Th'], ['Qd', 'Td'], ['Qc', 'Tc'], ['Qs', 'Ts'], ['Qh', '9h'], ['Qd', '9d'], ['Qc', '9c'], ['Qs', '9s'], ['Qh', '8h'], ['Qd', '8d'], ['Qc', '8c'], ['Qs', '8s'], 
                    ['Jh', 'Th'], ['Jd', 'Td'], ['Jc', 'Tc'], ['Js', 'Ts'], ['Jh', '9h'], ['Jd', '9d'], ['Jc', '9c'], ['Js', '9s'], ['Jh', '8h'], ['Jd', '8d'], ['Jc', '8c'], ['Js', '8s'], 
                    ['Th', '9h'], ['Td', '9d'], ['Tc', '9c'], ['Ts', '9s'], ['Th', '8h'], ['Td', '8d'], ['Tc', '8c'], ['Ts', '8s'], 
                    ['9h', '8h'], ['9d', '8d'], ['9c', '8c'], ['9s', '8s'], ['9h', '7h'], ['9d', '7d'], ['9c', '7c'], ['9s', '7s'], 
                    ['Ah', 'Kd'], ['Ah', 'Kc'], ['Ah', 'Ks'], ['Ad', 'Ks'], ['Ac', 'Kd'], ['Ac', 'Kh'], ['Ac', 'Ks'], ['As', 'Kd'], ['As', 'Kc'], ['As', 'Kh'], ['Ah', 'Qd'], ['Ah', 'Qc'], ['Ah', 'Qs'], ['Ad', 'Qs'], ['Ac', 'Qd'], ['Ac', 'Qh'], ['Ac', 'Qs'], ['As', 'Qd'], ['As', 'Qc'], ['As', 'Qh'], ['Ah', 'Jd'], ['Ah', 'Jc'], ['Ah', 'Js'], ['Ad', 'Js'], ['Ac', 'Jd'], ['Ac', 'Jh'], ['Ac', 'Js'], ['As', 'Jd'], ['As', 'Jc'], ['As', 'Jh'], ['Ah', 'Td'], ['Ah', 'Tc'], ['Ah', 'Ts'], ['Ad', 'Ts'], ['Ac', 'Td'], ['Ac', 'Th'], ['Ac', 'Ts'], ['As', 'Td'], ['As', 'Tc'], ['As', 'Th'], ['Ah', '9d'], ['Ah', '9c'], ['Ah', '9s'], ['Ad', '9s'], ['Ac', '9d'], ['Ac', '9h'], ['Ac', '9s'], ['As', '9d'], ['As', '9c'], ['As', '9h'], 
                    ['Kh', 'Qd'], ['Kh', 'Qc'], ['Kh', 'Qs'], ['Kd', 'Qs'], ['Kc', 'Qd'], ['Kc', 'Qh'], ['Kc', 'Qs'], ['Ks', 'Qd'], ['Ks', 'Qc'], ['Ks', 'Qh'], ['Kh', 'Jd'], ['Kh', 'Jc'], ['Kh', 'Js'], ['Kd', 'Js'], ['Kc', 'Jd'], ['Kc', 'Jh'], ['Kc', 'Js'], ['Ks', 'Jd'], ['Ks', 'Jc'], ['Ks', 'Jh'], ['Kh', 'Td'], ['Kh', 'Tc'], ['Kh', 'Ts'], ['Kd', 'Ts'], ['Kc', 'Td'], ['Kc', 'Th'], ['Kc', 'Ts'], ['Ks', 'Td'], ['Ks', 'Tc'], ['Ks', 'Th'], 
                    ['Qh', 'Jd'], ['Qh', 'Jc'], ['Qh', 'Js'], ['Qd', 'Js'], ['Qc', 'Jd'], ['Qc', 'Jh'], ['Qc', 'Js'], ['Qs', 'Jd'], ['Qs', 'Jc'], ['Qs', 'Jh'], ['Qh', 'Td'], ['Qh', 'Tc'], ['Qh', 'Ts'], ['Qd', 'Ts'], ['Qc', 'Td'], ['Qc', 'Th'], ['Qc', 'Ts'], ['Qs', 'Td'], ['Qs', 'Tc'], ['Qs', 'Th'], 
                    ['Jh', 'Td'], ['Jh', 'Tc'], ['Jh', 'Ts'], ['Jd', 'Ts'], ['Jc', 'Td'], ['Jc', 'Th'], ['Jc', 'Ts'], ['Js', 'Td'], ['Js', 'Tc'], ['Js', 'Th']]
            return self.compare_hand_with_range(cards, range, action)
        elif(player.uuid == '7'):
            range = [['Ah', 'Ad'], ['Ah', 'Ac'], ['Ah', 'As'], ['Ad', 'Ac'], ['Ad', 'As'], ['Ac', 'As'], 
                    ['Kh', 'Kd'], ['Kh', 'Kc'], ['Kh', 'Ks'], ['Kd', 'Kc'], ['Kd', 'Ks'], ['Kc', 'Ks'], 
                    ['Qh', 'Qd'], ['Qh', 'Qc'], ['Qh', 'Qs'], ['Qd', 'Qc'], ['Qd', 'Qs'], ['Qc', 'Qs'], 
                    ['Jh', 'Jd'], ['Jh', 'Jc'], ['Jh', 'Js'], ['Jd', 'Jc'], ['Jd', 'Js'], ['Jc', 'Js'], 
                    ['Th', 'Td'], ['Th', 'Tc'], ['Th', 'Ts'], ['Td', 'Tc'], ['Td', 'Ts'], ['Tc', 'Ts'], 
                    ['9h', '9d'], ['9h', '9c'], ['9h', '9s'], ['9d', '9c'], ['9d', '9s'], ['9c', '9s'], 
                    ['8h', '8d'], ['8h', '8c'], ['8h', '8s'], ['8d', '8c'], ['8d', '8s'], ['8c', '8s'], 
                    ['7h', '7d'], ['7h', '7c'], ['7h', '7s'], ['7d', '7c'], ['7d', '7s'], ['7c', '7s'], 
                    ['6h', '6d'], ['6h', '6c'], ['6h', '6s'], ['6d', '6c'], ['6d', '6s'], ['6c', '6s'], 
                    ['5h', '5d'], ['5h', '5c'], ['5h', '5s'], ['5d', '5c'], ['5d', '5s'], ['5c', '5s'], 
                    ['4h', '4d'], ['4h', '4c'], ['4h', '4s'], ['4d', '4c'], ['4d', '4s'], ['4c', '4s'], 
                    ['3h', '3d'], ['3h', '3c'], ['3h', '3s'], ['3d', '3c'], ['3d', '3s'], ['3c', '3s'], 
                    ['2h', '2d'], ['2h', '2c'], ['2h', '2s'], ['2d', '2c'], ['2d', '2s'], ['2c', '2s'], 
                    ['Ah', 'Kh'], ['Ad', 'Kd'], ['Ac', 'Kc'], ['As', 'Ks'], ['Ah', 'Qh'], ['Ad', 'Qd'], ['Ac', 'Qc'], ['As', 'Qs'], ['Ah', 'JKh'], ['Ad', 'JKd'], ['Ac', 'JKc'], ['As', 'JKs'], ['Ah', 'Th'], ['Ad', 'Td'], ['Ac', 'Tc'], ['As', 'Ts'], ['Ah', '9h'], ['Ad', '9d'], ['Ac', '9c'], ['As', '9s'], ['Ah', '8h'], ['Ad', '8d'], ['Ac', '8c'], ['As', '8s'], ['Ah', '7h'], ['Ad', '7d'], ['Ac', '7c'], ['As', '7s'], ['Ah', '6h'], ['Ad', '6d'], ['Ac', '6c'], ['As', '6s'], ['Ah', '5h'], ['Ad', '5d'], ['Ac', '5c'], ['As', '5s'], ['Ah', '4h'], ['Ad', '4d'], ['Ac', '4c'], ['As', '4s'], ['Ah', '3h'], ['Ad', '3d'], ['Ac', '3c'], ['As', '3s'], ['Ah', '3d'], ['Ah', '3c'], ['Ah', '3s'], ['Ad', '3c'], ['Ad', '3s'], ['Ac', '3s'], ['Ah', '2d'], ['Ah', '2c'], ['Ah', '2s'], ['Ad', '2c'], ['Ad', '2s'], ['Ac', '2s'], 
                    ['Kh', 'Qh'], ['Kd', 'Qd'], ['Kc', 'Qc'], ['Ks', 'Qs'], ['Kh', 'Jh'], ['Kd', 'Jd'], ['Kc', 'Jc'], ['Ks', 'Js'], ['Kh', 'Th'], ['Kd', 'Td'], ['Kc', 'Tc'], ['Ks', 'Ts'], ['Kh', '9h'], ['Kd', '9d'], ['Kc', '9c'], ['Ks', '9s'], ['Kh', '8h'], ['Kd', '8d'], ['Kc', '8c'], ['Ks', '8s'], ['Kh', '7h'], ['Kd', '7d'], ['Kc', '7c'], ['Ks', '7s'], ['Kh', '6h'], ['Kd', '6d'], ['Kc', '6c'], ['Ks', '6s'], ['Kh', '5h'], ['Kd', '5d'], ['Kc', '5c'], ['Ks', '5s'], ['Kh', '4h'], ['Kd', '4d'], ['Kc', '4c'], ['Ks', '4s'], ['Kh', '3h'], ['Kd', '3d'], ['Kc', '3c'], ['Ks', '3s'], ['Kh', '2h'], ['Kd', '2d'], ['Kc', '2c'], ['Ks', '2s'], 
                    ['Qh', 'Jh'], ['Qd', 'Jd'], ['Qc', 'Jc'], ['Qs', 'Js'], ['Qh', 'Th'], ['Qd', 'Td'], ['Qc', 'Tc'], ['Qs', 'Ts'], ['Qh', '9h'], ['Qd', '9d'], ['Qc', '9c'], ['Qs', '9s'], ['Qh', '8h'], ['Qd', '8d'], ['Qc', '8c'], ['Qs', '8s'], ['Qh', '7h'], ['Qd', '7d'], ['Qc', '7c'], ['Qs', '7s'], ['Qh', '6h'], ['Qd', '6d'], ['Qc', '6c'], ['Qs', '6s'], ['Qh', '5h'], ['Qd', '5d'], ['Qc', '5c'], ['Qs', '5s'], ['Qh', '4h'], ['Qd', '4d'], ['Qc', '4c'], ['Qs', '4s'], ['Qh', '3h'], ['Qd', '3d'], ['Qc', '3c'], ['Qs', '3s'], 
                    ['Jh', 'Th'], ['Jd', 'Td'], ['Jc', 'Tc'], ['Js', 'Ts'], ['Jh', '9h'], ['Jd', '9d'], ['Jc', '9c'], ['Js', '9s'], ['Jh', '8h'], ['Jd', '8d'], ['Jc', '8c'], ['Js', '8s'], ['Jh', '7h'], ['Jd', '7d'], ['Jc', '7c'], ['Js', '7s'], ['Jh', '6h'], ['Jd', '6d'], ['Jc', '6c'], ['Js', '6s'], ['Jh', '5h'], ['Jd', '5d'], ['Jc', '5c'], ['Js', '5s'], 
                    ['Th', '9h'], ['Td', '9d'], ['Tc', '9c'], ['Ts', '9s'], ['Th', '8h'], ['Td', '8d'], ['Tc', '8c'], ['Ts', '8s'], ['Th', '7h'], ['Td', '7d'], ['Tc', '7c'], ['Ts', '7s'], ['Th', '6h'], ['Td', '6d'], ['Tc', '6c'], ['Ts', '6s'], 
                    ['9h', '8h'], ['9d', '8d'], ['9c', '8c'], ['9s', '8s'], ['9h', '7h'], ['9d', '7d'], ['9c', '7c'], ['9s', '7s'], ['9h', '6h'], ['9d', '6d'], ['9c', '6c'], ['9s', '6s'], 
                    ['8h', '6h'], ['8d', '6d'], ['8c', '6c'], ['8s', '6s'], 
                    ['7h', '6h'], ['7d', '6d'], ['7c', '6c'], ['7s', '6s'], ['7h', '5h'], ['7d', '5d'], ['7c', '5c'], ['7s', '5s'], 
                    ['6h', '5h'], ['6d', '5d'], ['6c', '5c'], ['6s', '5s'], 
                    ['5h', '4h'], ['5d', '4d'], ['5c', '4c'], ['5s', '4s'], 
                    ['Ah', 'Kd'], ['Ah', 'Kc'], ['Ah', 'Ks'], ['Ad', 'Ks'], ['Ac', 'Kd'], ['Ac', 'Kh'], ['Ac', 'Ks'], ['As', 'Kd'], ['As', 'Kc'], ['As', 'Kh'], ['Ah', 'Qd'], ['Ah', 'Qc'], ['Ah', 'Qs'], ['Ad', 'Qs'], ['Ac', 'Qd'], ['Ac', 'Qh'], ['Ac', 'Qs'], ['As', 'Qd'], ['As', 'Qc'], ['As', 'Qh'], ['Ah', 'Jd'], ['Ah', 'Jc'], ['Ah', 'Js'], ['Ad', 'Js'], ['Ac', 'Jd'], ['Ac', 'Jh'], ['Ac', 'Js'], ['As', 'Jd'], ['As', 'Jc'], ['As', 'Jh'], ['Ah', 'Td'], ['Ah', 'Tc'], ['Ah', 'Ts'], ['Ad', 'Ts'], ['Ac', 'Td'], ['Ac', 'Th'], ['Ac', 'Ts'], ['As', 'Td'], ['As', 'Tc'], ['As', 'Th'], ['Ah', '9d'], ['Ah', '9c'], ['Ah', '9s'], ['Ad', '9s'], ['Ac', '9d'], ['Ac', '9h'], ['Ac', '9s'], ['As', '9d'], ['As', '9c'], ['As', '9h'], ['Ah', '8d'], ['Ah', '8c'], ['Ah', '8s'], ['Ad', '8s'], ['Ac', '8d'], ['Ac', '8h'], ['Ac', '8s'], ['As', '8d'], ['As', '8c'], ['As', '8h'], ['Ah', '7d'], ['Ah', '7c'], ['Ah', '7s'], ['Ad', '7s'], ['Ac', '7d'], ['Ac', '7h'], ['Ac', '7s'], ['As', '7d'], ['As', '7c'], ['As', '7h'], ['Ah', '6d'], ['Ah', '6c'], ['Ah', '6s'], ['Ad', '6s'], ['Ac', '6d'], ['Ac', '6h'], ['Ac', '6s'], ['As', '6d'], ['As', '6c'], ['As', '6h'], ['Ah', '5d'], ['Ah', '5c'], ['Ah', '5s'], ['Ad', '5s'], ['Ac', '5d'], ['Ac', '5h'], ['Ac', '5s'], ['As', '5d'], ['As', '5c'], ['As', '5h'], ['Ah', '4d'], ['Ah', '4c'], ['Ah', '4s'], ['Ad', '4s'], ['Ac', '4d'], ['Ac', '4h'], ['Ac', '4s'], ['As', '4d'], ['As', '4c'], ['As', '4h'], ['Ah', '3d'], ['Ah', '3c'], ['Ah', '3s'], ['Ad', '3s'], ['Ac', '3d'], ['Ac', '3h'], ['Ac', '3s'], ['As', '3d'], ['As', '3c'], ['As', '3h'], 
                    ['Kh', 'Qd'], ['Kh', 'Qc'], ['Kh', 'Qs'], ['Kd', 'Qs'], ['Kc', 'Qd'], ['Kc', 'Qh'], ['Kc', 'Qs'], ['Ks', 'Qd'], ['Ks', 'Qc'], ['Ks', 'Qh'], ['Kh', 'Jd'], ['Kh', 'Jc'], ['Kh', 'Js'], ['Kd', 'Js'], ['Kc', 'Jd'], ['Kc', 'Jh'], ['Kc', 'Js'], ['Ks', 'Jd'], ['Ks', 'Jc'], ['Ks', 'Jh'], ['Kh', 'Td'], ['Kh', 'Tc'], ['Kh', 'Ts'], ['Kd', 'Ts'], ['Kc', 'Td'], ['Kc', 'Th'], ['Kc', 'Ts'], ['Ks', 'Td'], ['Ks', 'Tc'], ['Ks', 'Th'], ['Kh', '9d'], ['Kh', '9c'], ['Kh', '9s'], ['Kd', '9s'], ['Kc', '9d'], ['Kc', '9h'], ['Kc', '9s'], ['Ks', '9d'], ['Ks', '9c'], ['Ks', '9h'], 
                    ['Qh', 'Jd'], ['Qh', 'Jc'], ['Qh', 'Js'], ['Qd', 'Js'], ['Qc', 'Jd'], ['Qc', 'Jh'], ['Qc', 'Js'], ['Qs', 'Jd'], ['Qs', 'Jc'], ['Qs', 'Jh'], ['Qh', 'Td'], ['Qh', 'Tc'], ['Qh', 'Ts'], ['Qd', 'Ts'], ['Qc', 'Td'], ['Qc', 'Th'], ['Qc', 'Ts'], ['Qs', 'Td'], ['Qs', 'Tc'], ['Qs', 'Th'], ['Qh', '9d'], ['Qh', '9c'], ['Qh', '9s'], ['Qd', '9s'], ['Qc', '9d'], ['Qc', '9h'], ['Qc', '9s'], ['Qs', '9d'], ['Qs', '9c'], ['Qs', '9h'], 
                    ['Jh', 'Td'], ['Jh', 'Tc'], ['Jh', 'Ts'], ['Jd', 'Ts'], ['Jc', 'Td'], ['Jc', 'Th'], ['Jc', 'Ts'], ['Js', 'Td'], ['Js', 'Tc'], ['Js', 'Th'], ['Jh', '9d'], ['Jh', '9c'], ['Jh', '9s'], ['Jd', '9s'], ['Jc', '9d'], ['Jc', '9h'], ['Jc', '9s'], ['Js', '9d'], ['Js', '9c'], ['Js', '9h'], 
                    ['Th', '9d'], ['Th', '9c'], ['Th', '9s'], ['Td', '9s'], ['Tc', '9d'], ['Tc', '9h'], ['Tc', '9s'], ['Ts', '9d'], ['Ts', '9c'], ['Ts', '9h']]
            return self.compare_hand_with_range(cards, range, action)
        elif(player.uuid == '1'):
            range = [['Ah', 'Ad'], ['Ah', 'Ac'], ['Ah', 'As'], ['Ad', 'Ac'], ['Ad', 'As'], ['Ac', 'As'], 
                    ['Kh', 'Kd'], ['Kh', 'Kc'], ['Kh', 'Ks'], ['Kd', 'Kc'], ['Kd', 'Ks'], ['Kc', 'Ks'], 
                    ['Qh', 'Qd'], ['Qh', 'Qc'], ['Qh', 'Qs'], ['Qd', 'Qc'], ['Qd', 'Qs'], ['Qc', 'Qs'], 
                    ['Jh', 'Jd'], ['Jh', 'Jc'], ['Jh', 'Js'], ['Jd', 'Jc'], ['Jd', 'Js'], ['Jc', 'Js'], 
                    ['Th', 'Td'], ['Th', 'Tc'], ['Th', 'Ts'], ['Td', 'Tc'], ['Td', 'Ts'], ['Tc', 'Ts'], 
                    ['9h', '9d'], ['9h', '9c'], ['9h', '9s'], ['9d', '9c'], ['9d', '9s'], ['9c', '9s'], 
                    ['8h', '8d'], ['8h', '8c'], ['8h', '8s'], ['8d', '8c'], ['8d', '8s'], ['8c', '8s'], 
                    ['7h', '7d'], ['7h', '7c'], ['7h', '7s'], ['7d', '7c'], ['7d', '7s'], ['7c', '7s'], 
                    ['6h', '6d'], ['6h', '6c'], ['6h', '6s'], ['6d', '6c'], ['6d', '6s'], ['6c', '6s'], 
                    ['5h', '5d'], ['5h', '5c'], ['5h', '5s'], ['5d', '5c'], ['5d', '5s'], ['5c', '5s'], 
                    ['4h', '4d'], ['4h', '4c'], ['4h', '4s'], ['4d', '4c'], ['4d', '4s'], ['4c', '4s'], 
                    ['3h', '3d'], ['3h', '3c'], ['3h', '3s'], ['3d', '3c'], ['3d', '3s'], ['3c', '3s'], 
                    ['2h', '2d'], ['2h', '2c'], ['2h', '2s'], ['2d', '2c'], ['2d', '2s'], ['2c', '2s'], 
                    ['Ah', 'Kh'], ['Ad', 'Kd'], ['Ac', 'Kc'], ['As', 'Ks'], ['Ah', 'Qh'], ['Ad', 'Qd'], ['Ac', 'Qc'], ['As', 'Qs'], ['Ah', 'JKh'], ['Ad', 'JKd'], ['Ac', 'JKc'], ['As', 'JKs'], ['Ah', 'Th'], ['Ad', 'Td'], ['Ac', 'Tc'], ['As', 'Ts'], ['Ah', '9h'], ['Ad', '9d'], ['Ac', '9c'], ['As', '9s'], ['Ah', '8h'], ['Ad', '8d'], ['Ac', '8c'], ['As', '8s'], ['Ah', '7h'], ['Ad', '7d'], ['Ac', '7c'], ['As', '7s'], ['Ah', '6h'], ['Ad', '6d'], ['Ac', '6c'], ['As', '6s'], ['Ah', '5h'], ['Ad', '5d'], ['Ac', '5c'], ['As', '5s'], ['Ah', '4h'], ['Ad', '4d'], ['Ac', '4c'], ['As', '4s'], ['Ah', '3h'], ['Ad', '3d'], ['Ac', '3c'], ['As', '3s'], ['Ah', '3d'], ['Ah', '3c'], ['Ah', '3s'], ['Ad', '3c'], ['Ad', '3s'], ['Ac', '3s'], ['Ah', '2d'], ['Ah', '2c'], ['Ah', '2s'], ['Ad', '2c'], ['Ad', '2s'], ['Ac', '2s'], 
                    ['Kh', 'Qh'], ['Kd', 'Qd'], ['Kc', 'Qc'], ['Ks', 'Qs'], ['Kh', 'Jh'], ['Kd', 'Jd'], ['Kc', 'Jc'], ['Ks', 'Js'], ['Kh', 'Th'], ['Kd', 'Td'], ['Kc', 'Tc'], ['Ks', 'Ts'], ['Kh', '9h'], ['Kd', '9d'], ['Kc', '9c'], ['Ks', '9s'], ['Kh', '8h'], ['Kd', '8d'], ['Kc', '8c'], ['Ks', '8s'], ['Kh', '7h'], ['Kd', '7d'], ['Kc', '7c'], ['Ks', '7s'], ['Kh', '6h'], ['Kd', '6d'], ['Kc', '6c'], ['Ks', '6s'], ['Kh', '5h'], ['Kd', '5d'], ['Kc', '5c'], ['Ks', '5s'], ['Kh', '4h'], ['Kd', '4d'], ['Kc', '4c'], ['Ks', '4s'], ['Kh', '3h'], ['Kd', '3d'], ['Kc', '3c'], ['Ks', '3s'], ['Kh', '2h'], ['Kd', '2d'], ['Kc', '2c'], ['Ks', '2s'], 
                    ['Qh', 'Jh'], ['Qd', 'Jd'], ['Qc', 'Jc'], ['Qs', 'Js'], ['Qh', 'Th'], ['Qd', 'Td'], ['Qc', 'Tc'], ['Qs', 'Ts'], ['Qh', '9h'], ['Qd', '9d'], ['Qc', '9c'], ['Qs', '9s'], ['Qh', '8h'], ['Qd', '8d'], ['Qc', '8c'], ['Qs', '8s'], ['Qh', '7h'], ['Qd', '7d'], ['Qc', '7c'], ['Qs', '7s'], ['Qh', '6h'], ['Qd', '6d'], ['Qc', '6c'], ['Qs', '6s'], ['Qh', '5h'], ['Qd', '5d'], ['Qc', '5c'], ['Qs', '5s'], ['Qh', '4h'], ['Qd', '4d'], ['Qc', '4c'], ['Qs', '4s'], ['Qh', '3h'], ['Qd', '3d'], ['Qc', '3c'], ['Qs', '3s'], 
                    ['Jh', 'Th'], ['Jd', 'Td'], ['Jc', 'Tc'], ['Js', 'Ts'], ['Jh', '9h'], ['Jd', '9d'], ['Jc', '9c'], ['Js', '9s'], ['Jh', '8h'], ['Jd', '8d'], ['Jc', '8c'], ['Js', '8s'], ['Jh', '7h'], ['Jd', '7d'], ['Jc', '7c'], ['Js', '7s'], ['Jh', '6h'], ['Jd', '6d'], ['Jc', '6c'], ['Js', '6s'], ['Jh', '5h'], ['Jd', '5d'], ['Jc', '5c'], ['Js', '5s'], 
                    ['Th', '9h'], ['Td', '9d'], ['Tc', '9c'], ['Ts', '9s'], ['Th', '8h'], ['Td', '8d'], ['Tc', '8c'], ['Ts', '8s'], ['Th', '7h'], ['Td', '7d'], ['Tc', '7c'], ['Ts', '7s'], ['Th', '6h'], ['Td', '6d'], ['Tc', '6c'], ['Ts', '6s'], 
                    ['9h', '8h'], ['9d', '8d'], ['9c', '8c'], ['9s', '8s'], ['9h', '7h'], ['9d', '7d'], ['9c', '7c'], ['9s', '7s'], ['9h', '6h'], ['9d', '6d'], ['9c', '6c'], ['9s', '6s'], 
                    ['8h', '6h'], ['8d', '6d'], ['8c', '6c'], ['8s', '6s'], 
                    ['7h', '6h'], ['7d', '6d'], ['7c', '6c'], ['7s', '6s'], ['7h', '5h'], ['7d', '5d'], ['7c', '5c'], ['7s', '5s'], 
                    ['6h', '5h'], ['6d', '5d'], ['6c', '5c'], ['6s', '5s'], 
                    ['5h', '4h'], ['5d', '4d'], ['5c', '4c'], ['5s', '4s'], 
                    ['Ah', 'Kd'], ['Ah', 'Kc'], ['Ah', 'Ks'], ['Ad', 'Ks'], ['Ac', 'Kd'], ['Ac', 'Kh'], ['Ac', 'Ks'], ['As', 'Kd'], ['As', 'Kc'], ['As', 'Kh'], ['Ah', 'Qd'], ['Ah', 'Qc'], ['Ah', 'Qs'], ['Ad', 'Qs'], ['Ac', 'Qd'], ['Ac', 'Qh'], ['Ac', 'Qs'], ['As', 'Qd'], ['As', 'Qc'], ['As', 'Qh'], ['Ah', 'Jd'], ['Ah', 'Jc'], ['Ah', 'Js'], ['Ad', 'Js'], ['Ac', 'Jd'], ['Ac', 'Jh'], ['Ac', 'Js'], ['As', 'Jd'], ['As', 'Jc'], ['As', 'Jh'], ['Ah', 'Td'], ['Ah', 'Tc'], ['Ah', 'Ts'], ['Ad', 'Ts'], ['Ac', 'Td'], ['Ac', 'Th'], ['Ac', 'Ts'], ['As', 'Td'], ['As', 'Tc'], ['As', 'Th'], ['Ah', '9d'], ['Ah', '9c'], ['Ah', '9s'], ['Ad', '9s'], ['Ac', '9d'], ['Ac', '9h'], ['Ac', '9s'], ['As', '9d'], ['As', '9c'], ['As', '9h'], ['Ah', '8d'], ['Ah', '8c'], ['Ah', '8s'], ['Ad', '8s'], ['Ac', '8d'], ['Ac', '8h'], ['Ac', '8s'], ['As', '8d'], ['As', '8c'], ['As', '8h'], ['Ah', '7d'], ['Ah', '7c'], ['Ah', '7s'], ['Ad', '7s'], ['Ac', '7d'], ['Ac', '7h'], ['Ac', '7s'], ['As', '7d'], ['As', '7c'], ['As', '7h'], ['Ah', '6d'], ['Ah', '6c'], ['Ah', '6s'], ['Ad', '6s'], ['Ac', '6d'], ['Ac', '6h'], ['Ac', '6s'], ['As', '6d'], ['As', '6c'], ['As', '6h'], ['Ah', '5d'], ['Ah', '5c'], ['Ah', '5s'], ['Ad', '5s'], ['Ac', '5d'], ['Ac', '5h'], ['Ac', '5s'], ['As', '5d'], ['As', '5c'], ['As', '5h'], ['Ah', '4d'], ['Ah', '4c'], ['Ah', '4s'], ['Ad', '4s'], ['Ac', '4d'], ['Ac', '4h'], ['Ac', '4s'], ['As', '4d'], ['As', '4c'], ['As', '4h'], ['Ah', '3d'], ['Ah', '3c'], ['Ah', '3s'], ['Ad', '3s'], ['Ac', '3d'], ['Ac', '3h'], ['Ac', '3s'], ['As', '3d'], ['As', '3c'], ['As', '3h'], 
                    ['Kh', 'Qd'], ['Kh', 'Qc'], ['Kh', 'Qs'], ['Kd', 'Qs'], ['Kc', 'Qd'], ['Kc', 'Qh'], ['Kc', 'Qs'], ['Ks', 'Qd'], ['Ks', 'Qc'], ['Ks', 'Qh'], ['Kh', 'Jd'], ['Kh', 'Jc'], ['Kh', 'Js'], ['Kd', 'Js'], ['Kc', 'Jd'], ['Kc', 'Jh'], ['Kc', 'Js'], ['Ks', 'Jd'], ['Ks', 'Jc'], ['Ks', 'Jh'], ['Kh', 'Td'], ['Kh', 'Tc'], ['Kh', 'Ts'], ['Kd', 'Ts'], ['Kc', 'Td'], ['Kc', 'Th'], ['Kc', 'Ts'], ['Ks', 'Td'], ['Ks', 'Tc'], ['Ks', 'Th'], ['Kh', '9d'], ['Kh', '9c'], ['Kh', '9s'], ['Kd', '9s'], ['Kc', '9d'], ['Kc', '9h'], ['Kc', '9s'], ['Ks', '9d'], ['Ks', '9c'], ['Ks', '9h'], 
                    ['Qh', 'Jd'], ['Qh', 'Jc'], ['Qh', 'Js'], ['Qd', 'Js'], ['Qc', 'Jd'], ['Qc', 'Jh'], ['Qc', 'Js'], ['Qs', 'Jd'], ['Qs', 'Jc'], ['Qs', 'Jh'], ['Qh', 'Td'], ['Qh', 'Tc'], ['Qh', 'Ts'], ['Qd', 'Ts'], ['Qc', 'Td'], ['Qc', 'Th'], ['Qc', 'Ts'], ['Qs', 'Td'], ['Qs', 'Tc'], ['Qs', 'Th'], ['Qh', '9d'], ['Qh', '9c'], ['Qh', '9s'], ['Qd', '9s'], ['Qc', '9d'], ['Qc', '9h'], ['Qc', '9s'], ['Qs', '9d'], ['Qs', '9c'], ['Qs', '9h'], 
                    ['Jh', 'Td'], ['Jh', 'Tc'], ['Jh', 'Ts'], ['Jd', 'Ts'], ['Jc', 'Td'], ['Jc', 'Th'], ['Jc', 'Ts'], ['Js', 'Td'], ['Js', 'Tc'], ['Js', 'Th'], ['Jh', '9d'], ['Jh', '9c'], ['Jh', '9s'], ['Jd', '9s'], ['Jc', '9d'], ['Jc', '9h'], ['Jc', '9s'], ['Js', '9d'], ['Js', '9c'], ['Js', '9h'], 
                    ['Th', '9d'], ['Th', '9c'], ['Th', '9s'], ['Td', '9s'], ['Tc', '9d'], ['Tc', '9h'], ['Tc', '9s'], ['Ts', '9d'], ['Ts', '9c'], ['Ts', '9h']]
            return self.compare_hand_with_range(cards, range, action)
        elif(player.uuid == '2'):
            print("BB RFI ERR")
            return 0
        else:
            print("PREFLOP RFI() ERROR")
            return 0
    
    def compare_hand_with_range(self, cards, range, action):
        reward = 0
        for hand in range:
            if((cards[0] == hand[0] and cards[1] == hand[1]) or (cards[1] == hand[0] and cards[0] == hand[1])):
                #print("TRUE")
                if(action == "raise"):
                    #reward
                    reward = 100
                    #print("GOOD RAISE")
                    
                elif(action == "fold"):
                    #punish
                    reward = -100
                    #print("BAD FOLD, SHOULD HAVE RAISED")
                    
                elif(action) == "call":
                    reward = -1
                    #punish
                    #print("BAD CALL, SHOULD HAVE RAISED")

                print("IN RANGE", reward)
                return reward 
                    
            else:
                #print("FALSE")
                if(action == "raise"):
                    #punish
                    reward = -100
                    #print("BAD RAISE, SHOULD HAVE FOLD")
                    
                elif(action == "fold"):
                    #reward
                    reward = 100
                    #print("GOOD FOLD")
                    
                elif(action) == "call":
                    #punish
                    reward = -1
                    #print("BAD CALL, SHOULD HAVE FOLD")  
                    
        print("NOT IN RANGE", reward)
        return reward
    

# Create the environment
env = PokerGymEnv()

# Train an RL agent using PPO
model = PPO("MlpPolicy", env, verbose=1)
model.learn(total_timesteps=100000)
model.save("ppo_poker_agent")

# Test the agent
model = PPO.load("ppo_poker_agent")
obs = env.reset()
done = False
while not done:
    action, _states = model.predict(obs)
    obs, reward, done, info = env.step(action)
    #print(f"Action: {action}, Reward: {reward}")
