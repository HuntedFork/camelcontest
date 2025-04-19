from typing import List, Dict



############################Game State#######################
class BettingTile:
    color: str
    value: int

class SpectatorTile:
    player_name: str
    space_number: int
    cheering: bool # False means the camels move backwards

class Camel:
    color: str
    position: int # board position (1–16)
    stack_position: int # 0 = bottom, higher = stacked above
    betting_tiles: List[BettingTile]

class Player:
    name: str
    money: int
    betting_tiles: List[BettingTile]

# This is the complete state of the camel up game
# Please feel free to add useful sounding getters
# Final bets are changed to 'hidden' for other players before being sent to you
class GameState:
    track_length = 16
    colors = ['blue', 'red', 'green', 'yellow', 'white']
    betting_tile_ranks = [2,2,3,5]
    final_bet_scoring = [8, 5, 3, 2, 1]

    def __init__(
        self,
        camels: List[Camel],
        players: Dict[str, Player],
        dice_pool: List[str],
        rolled_dice: List[str],
        spectator_tiles: List[SpectatorTile],
        final_win_bet: List[tuple[str, str]],
        final_lose_bet: List[tuple[str, str]],
        game_over: bool,
    ):
        self.camels = camels
        self.players = players
        self.dice_pool = dice_pool
        self.rolled_dice = rolled_dice
        self.spectator_tiles = spectator_tiles
        self.final_win_bet = final_win_bet
        self.final_lose_bet = final_lose_bet
        self.game_over = game_over

    def get_camel(self, color):
        for camel in self.camels:
            if camel.color == color:
                return camel
    
    def get_camels_by_winning(self):
        return sorted(self.camels, key=lambda x: (x.position, x.stack_position), reverse=True)
    
    def get_camels_on_space(self, space_number):
        camels = [camel for camel in self.camels if camel.position == space_number]
        camels.sort(key=lambda x: x.stack_position)
        return camels
    
    def get_spectator_tile(self, space_number):
        for tile in self.spectator_tiles:
            if tile.space_number == space_number:
                return tile
        return None
    
    # TODO: Add useful getters for players
    # Like "have what final bets have I placed already?"

    
    def __repr__(self):
        lines = [""]
        lines.append("=== Camel Up Game State ===")

        # Show camels by position, sorted for clarity
        position_map: Dict[int, List[Camel]] = {}
        for camel in self.camels:
            position_map.setdefault(camel.position, []).append(camel)

        for pos in sorted(position_map.keys()):
            stack = sorted(position_map[pos], key=lambda c: c.stack_position)
            stack_str = "/".join(c.color for c in stack)
            lines.append(f"Space {pos}: {stack_str}")

        lines.append("\nPlayers:")
        for player in self.players.values():
            lines.append(
                f"  {player.name}: ${player.money}, "
                f"Leg Bets: {player.betting_tiles}, "
            )

        lines.append("\nRemaining Dice: " + ", ".join(self.dice_pool))
        lines.append("Rolled Dice: " + ", ".join(self.rolled_dice))
        lines.append("Final Win Bets: " + ", ".join([str(x) for x in self.final_win_bet]))
        lines.append("Final Lose Bets: " + ", ".join([str(x) for x in self.final_lose_bet]))
        lines.append(f"Game Over: {self.game_over}")
        lines.append("")
        return "\n".join(lines)

###### Turn Definitions ######
# Abstract, dont use
class Turn:
    def __init__(self, action):
        self.action = action

# Roll the dice!
class Roll(Turn):
    def __init__(self):
        super().__init__("roll")

# Take a betting tile
# You cant take from an empty betting tile stack
class LegBet(Turn):
    def __init__(self, color: str):
        super().__init__("legbet")
        self.color = color

# Place your spectating tile.
# Spectating tiles cannot be placed on spots with camels
# Or within one space of another spectating tile
class Spectate(Turn):
    def __init__(self, spot_number: int, cheering: bool):
        super().__init__("spectate")
        self.spot_number = spot_number
        self.cheering = cheering

# Bet on the overal Winner (or loser) of the race
# You cant bet on the same color twice
class FinalBet(Turn):
    def __init__(self, color:str, win:bool):
        super().__init__("final")
        self.color = color
        self.win = win

# You have to implement one of these
class Brain:
    def __init__(self, name):
        self.name = name

    def take_turn(self, game: GameState) -> Turn:
        raise NotImplementedError()