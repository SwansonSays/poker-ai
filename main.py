from stable_baselines3 import PPO
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from pypokerengine.players import BasePokerPlayer
from pypokerengine.api.emulator import Emulator
import pypokerengine.engine.action_checker as Action
import random
from treys import Card, Deck, Evaluator

from state_builder import StateBuilder
from reward import Reward

class PokerGymEnv(gym.Env):
    def __init__(self, num_players=7):
        super(PokerGymEnv, self).__init__()

        # Define action space (fold, call, raise)
        self.action_space = spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)

        # Define observation space (agent's hand, community cards, stack sizes)
        self.observation_space = spaces.Box(low=0, high=1, shape=(831,), dtype=np.float32)

        self.state = None

        self.render_mode = "human"

        self.state_builder = StateBuilder()
        
        #idk about rewards
        self.reward = Reward()

    def reset(self, seed=None):
        print("         * * * * * * * *")
        print("         *  NEW GAME!  *")
        print("         * * * * * * * *","\n")

        self.state = self.state_builder.create_initial_state()

        print(self.state)

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
