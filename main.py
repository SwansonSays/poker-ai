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
        reward = self.calculate_reward()
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
        #print("Player: ", self.game_state["next_player"], action_name, amount)
        #print("POT: ", self.events[0]["round_state"]["pot"]["main"]['amount'])

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

    def calculate_reward(self):
        self.get_street()
        if(self.game_state["next_player"] != "not_found"): # != to new game/ new street event
            hole_cards = self.get_players_cards(self.get_player(self.game_state["next_player"]))
        else:
            return 0
        
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
        if(player.name == 1):
            range = []
            self.compare_hand_with_range(cards, range, action)
        elif(player.name == 2):
            range = []
            self.compare_hand_with_range(cards, range, action)
        elif(player.name == 3):
            range = []
            self.compare_hand_with_range(cards, range, action)
        elif(player.name == 4):
            range = []
            self.compare_hand_with_range(cards, range, action)
        elif(player.name == 5):
            range = []
            self.compare_hand_with_range(cards, range, action)
        elif(player.name == 6):
            range = []
            self.compare_hand_with_range(cards, range, action)
        elif(player.name == 7):
            range = []
            self.compare_hand_with_range(cards, range, action)
        else:
            print("ERROR")
    
    def compare_hand_with_range(self, cards, range, action):
        for hand in range:
            if((cards[0] == hand[0] and cards[1] == hand[1]) or (cards[1] == hand[0] and cards[0] == hand[1])):
                if(action == "raise"):
                    #reward
                    pass
                elif(action == "fold"):
                    #punish
                    pass
                elif(action) == "call":
                    #punish 
                    pass
            else:
                if(action == "raise"):
                    #punish
                    pass
                elif(action == "fold"):
                    #reward
                    pass
                elif(action) == "call":
                    #punish 
                    pass
    

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
