from stable_baselines3 import PPO
import gymnasium as gym
from gymnasium import spaces
import numpy as np
from pypokerengine.players import BasePokerPlayer
from pypokerengine.api.emulator import Emulator
import pypokerengine.engine.action_checker as Action
import random
from treys import Card, Deck, Evaluator

from obs_builder import ObsBuilder
from game_manager import GameManager
from reward import Reward

class PokerGymEnv(gym.Env):
    def __init__(self, num_players=7):
        super(PokerGymEnv, self).__init__()

        # Define action space (fold, call, raise)
        self.action_space = spaces.Box(low=0.0, high=1.0, shape=(1,), dtype=np.float32)

        # Define observation space (agent's hand, community cards, stack sizes)
        self.observation_space = spaces.Box(low=0, high=1, shape=(831,), dtype=np.float32)

        self.render_mode = "human"

        self.obs_builder = ObsBuilder()
        self.game_manager = GameManager(num_players)
        self.reward = Reward()

    def reset(self, seed=None):
        print("         * * * * * * * *")
        print("         *  NEW GAME!  *")
        print("         * * * * * * * *","\n")

        # Game manager to create game and returns init game state
        game_state, events = self.game_manager.create_game()
        
        # Obs builder takes game state and builds obs
        observation = self.obs_builder.build_observation(game_state, events)

        # Set Render mode
        if self.render_mode == "human":
            self.render()

        # Return observation
        return observation, {}

    def step(self, action):
        # 1. Check Winners -> Game Manager
        if(self.game_manager.check_winners()):
            done = True
            self.reset()
        else:
            done = False
        # 2. Get possible actions based off of current game state -> Game Manager
        possible_actions = self.game_manager.get_possible_actions()
        # 3. Decode the action and amount based off possible actions -> Obs Builder?
        action_name, amount = self.obs_builder.decode_action(action, possible_actions)
        # 4. Calculate the Reward -> Reward
        reward = self.reward.calculate_reward(action_name)
        # 5. Take action -> Game Manager
        game_state, events = self.game_manager.take_action(action_name, amount)
        # 6. Check Winners?
        if(self.game_manager.check_winners()):
            done = True
            self.reset()
        else:
            done = False
        # 7. Build Observation from Game State -> Obs Builder
        observation = self.obs_builder.build_observation(game_state, events)
        # 8. Render step
        if self.render_mode == "human":
            self.render(action_name, amount, reward)
        # 8. Return new Obs and reward and flag 
        return observation, reward, done, False, {}

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
