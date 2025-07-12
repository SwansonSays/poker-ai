from treys import Card, Deck, Evaluator

class Reward():
    def __init__(self):
        self.reward = 0
        self.hole_cards = []
        self.board = []
        self.street = None
        self.player = None
        self.action = None

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

                    hero_score = evaluator.evaluate(hand, full_board)
                    villian_score = evaluator.evaluate(opponent_hand, full_board)

                    if hero_score < villian_score:
                        wins += 1
                        wins_by_player[int(i/2)] += 1
            i += 2

        for i in range(len(wins_by_player)):
            wins_by_player[i] = round(wins_by_player[i] / simulations * 100, 2)
        
        return wins/simulations
    
    def preflop_rfi(self, player, action):
        cards = self.get_players_cards(player)

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