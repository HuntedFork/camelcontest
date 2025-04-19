from typing import List, Dict, Optional
import time
import random
from brains.api import GameState

class BettingTile:
    def __init__(self, color, value):
        self.color = color
        self.value = value

def new_betting_tile_stack(color):
    return [BettingTile(color, payout) for payout in [2,2,3,5]]

class SpectatorTile:
    def __init__(self, player_name, space_number, cheering):
        self.player_name:str = player_name
        self.space_number:int = space_number
        self.cheering:bool = cheering

class Camel:
    def __init__(self, color: str):
        self.color = color
        self.position = 0  # board position (1–16)
        self.stack_position = 0  # 0 = bottom, higher = stacked above
        self.betting_tiles:List[BettingTile] = new_betting_tile_stack(color) # payouts available for betting on this camel

    def end_of_leg(self):
        self.betting_tickets = new_betting_tile_stack(self.color)

class Player:
    def __init__(self, name: str):
        self.name = name
        self.money = 3
        self.betting_tiles: List[BettingTile] = [] 

class CamelUpGame(GameState):
    def __init__(self, player_names: List[str]):
        self.track_length = 16
        self.colors = ['blue', 'red', 'green', 'yellow', 'white']
        self.betting_tile_ranks = [2,2,3,5]
        self.final_bet_scoring = [8, 5, 3, 2, 1]



        self.camels: List[Camel] = [Camel(color) for color in self.colors]
        self.players: Dict[str, Player] = {name: Player(name) for name in player_names}
        self.dice_pool: List[str] = self.colors.copy()
        self.rolled_dice: List[str] = []
        self.spectator_tiles: List[SpectatorTile] = []
        self.final_win_bet: List[tuple[str,str]] = [] # [(player_name, color)]
        self.final_lose_bet: List[tuple[str,str]] = [] # [(player_name, color)]
        self.game_over = False
        self.place_initial_camels()


    #################### Game Actions ####################
    def roll_dice(self, player_name):
        player = self.players[player_name]
        print(player_name, " rolls the dice and gets 1 coin!")
        player.money += 1

        random.shuffle(self.dice_pool)
        die = self.dice_pool.pop()
        number = random.randint(1,3)
        print(die, " ", number, " was rolled!")
        self.rolled_dice.append(die)
        self.move_camel(die, number)
        if self.is_end_condition_met():
            self.game_over = True
            return
        if self.is_leg_over():
            self.end_leg()

    def take_betting_tile(self, player_name, color):
        camel = self.get_camel(color)
        player = self.players[player_name]
        if len(camel.betting_tiles) == 0:
            print(player_name, " tried to take a betting tile from an empty stack! ", color)
            return
        tile = camel.betting_tiles.pop()
        player.betting_tiles.append(tile)
        print(player_name, " is placing a bet on ", color, " for ", tile.value) 
    
    def place_spectator_tile(self, player_name:str, space_number:int, cheering:bool):
        # Check Legality
        camels_on_space = self.get_camels_on_space(space_number)
        if len(camels_on_space) > 0:
            print(player_name, "tried to place a spectator tile on spot with camels: ", space_number)
            return
        spectator_check_prev = self.get_spectator_tile(space_number - 1)
        spectator_check = self.get_spectator_tile(space_number)
        spectator_check_next = self.get_spectator_tile(space_number + 1)
        if spectator_check != None or spectator_check_prev != None or spectator_check_next != None:
            print(player_name, " tried to place a spectator tile on or next to a space that already has one: ", space_number)
            return
        for tile in self.spectator_tiles:
            if tile.player_name == player_name:
                print(player_name, " tried to place a second spectator tile!")
                return

        print(player_name, " is ", "cheering" if cheering else "booing", " space ", space_number)
        tile = SpectatorTile(player_name, space_number, cheering)
        self.spectator_tiles.append(tile)

    def bet_final_bet(self, player_name, color, win:bool):
        # Check final bet legality
        player = self.players[player_name]
        my_placed_colors = [bet[1] for bet in self.final_win_bet + self.final_win_bet if bet[0] == player_name]
        if color in my_placed_colors:
            print(player_name, " tried to place duplicate final bet! ", color)
            return
        if win:
            self.final_win_bet.append((player_name, color))
        else:
            self.final_lose_bet.append((player_name, color))
        print(player_name, "placed a final bet that ", color, " will ", "win" if win else "lose")


    ################# Helper Game Actions ###########################

    def place_initial_camels(self):
        for camel in self.camels:
            position = random.randint(1,3)
            stack_position = len(self.get_camels_on_space(position))
            camel.position = position
            camel.stack_position = stack_position

        
    def move_camel(self, camel_color, number):
        # Find our camel
        camel = self.get_camel(camel_color)
        # Find camel stack
        space = self.get_camels_on_space(camel.position)
        camel_stack = [x for x in space if x.stack_position >= camel.stack_position]
        # Check target for spectator tile
        target_space = camel.position + number
        spectator = self.get_spectator_tile(target_space)
        inverted = False # Should camels go on bottom? (Happens when booed)
        if spectator != None:
            player = self.players[spectator.player_name]
            print(player.name, " gets 1 coin since camels landed on their spectator tile!")
            player.money += 1
            if spectator.cheering:
                target_space += 1
            else:
                target_space -= 1
                inverted = True        
        camels_already_on_target_space = self.get_camels_on_space(target_space)
        # move camels
        for camel in camel_stack:
            camel.position = target_space
        #reorder camel stack
        new_camel_stack: List[Camel] = []
        if inverted:
            new_camel_stack = camel_stack + camels_already_on_target_space
        else:
            new_camel_stack = camels_already_on_target_space + camel_stack
        i = 0
        for camel in new_camel_stack:
            camel.stack_position = i
            i += 1
        # Set new positions and stack_positions

    def end_leg(self):
        lines = []
        lines.append("========End of Leg Scoring========")
        # Award betting ticket points
        for player in self.players.values():
            lines.append(player.name + ": ")
            for tile in player.betting_tiles:
                number = self.get_tile_score(tile)
                lines.append("    gained " + str(number) + " coins for betting on " + tile.color)
                player.money += number
            player.betting_tiles = []
        lines.append("====================================")
        print("\n".join(lines))
        for camel in self.camels:
            camel.betting_tiles = new_betting_tile_stack(camel.color)
        # Reset Spectator tiles
        self.spectator_tiles = []
        # Reset dice pool
        self.rolled_dice = []
        self.dice_pool = self.colors.copy()

    def end_game(self):
        print("++++++++++++++The Game Is Over+++++++++++++")
        self.end_leg()
        standings = [camel.color for camel in self.get_camels_by_winning()]
        winner = standings[0]
        loser = standings[-1]
        print("Final Camel Standings: ", standings)
        print("Winner: " + winner)
        print("Loser: ", loser)
        print("\n")
        print("Overal Loss Bet Scoring:")
        self.process_final_bet_pile(self.final_lose_bet, loser)
        print(" ")
        print("Overall Win Bet Scoring:")
        self.process_final_bet_pile(self.final_win_bet, winner)
        print(" ")
        players = sorted(self.players.values(), key=lambda x: x.money, reverse=True)
        print("AND")
        time.sleep(0.25)
        print("THE")
        time.sleep(0.25)
        print("WINNER")
        time.sleep(0.25)
        print("IS")
        time.sleep(0.5)
        print(players[0].name, "!!!!!!!!!!!")
        time.sleep(1)
        print("")
        print("Final Scores:")
        for player in players:
            print(player.name, ": ", player.money)
        print("GG")


    
    def process_final_bet_pile(self, bets, target_color):
        i = 0
        for bet in bets:
            player_name = bet[0]
            color = bet[1]
            if color == target_color:
                number = self.get_final_bet_score(i)
                i += 1
            else:
                number = -1
            print("    ", player_name, " got ", number, " coins for betting on ", color)
            player = self.players[player_name]
            player.money += number
    
    ######## Private Getters ################
    # Before adding here make sure the players dont want to access them

    def is_end_condition_met(self):
        for camel in self.camels:
            if camel.position > 16:
                return True
        return False
    
    def is_leg_over(self):
        return len(self.dice_pool) == 0
    
    def get_tile_score(self, tile:BettingTile):
        camel_order = self.get_camels_by_winning()
        number = -1
        if tile.color == camel_order[0].color:
            number = tile.value
        if tile.color == camel_order[1].color:
            number = 1
        return number
    
    def get_final_bet_score(self, number_of_other_bets):
        if number_of_other_bets > len(self.final_bet_scoring):
            return 1
        else:
            return self.final_bet_scoring[number_of_other_bets]
    # Need to pass the player something they can modify that has hidden information hidden
    def get_private_gamestate(self, player_name):
        gamestate = GameState(
            camels=self.camels,
            players=self.players,
            dice_pool=self.dice_pool,
            rolled_dice=self.rolled_dice,
            spectator_tiles=self.spectator_tiles,
            final_win_bet=self.privatize_bets(self.final_win_bet, player_name),
            final_lose_bet=self.privatize_bets(self.final_lose_bet,player_name),
            game_over=self.game_over
        )
        return gamestate
    
    def privatize_bets(self, bets:List[tuple[str, str]], player_name):
        return [bet if bet[0] == player_name else (bet[0], 'hidden') for bet in bets]

if __name__ == '__main__':
    game = CamelUpGame(['forrest', 'luke'])
    game.roll_dice('forrest')
    game.bet_final_bet('forrest', 'red', True)
    game.bet_final_bet('luke', 'blue', False)
    print(game.get_private_gamestate('forrest'))
    