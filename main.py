import random
import itertools
from game import CamelUpGame
from brains.api import Brain
from brains.rollbrain import RollBrain


players = [
    RollBrain("RollerDogger"),
    RollBrain("RollerCat")
]

if __name__ == "__main__":
    names = [brain.name for brain in players]
    game = CamelUpGame(names)
    random.shuffle(players)
    for player in itertools.cycle(players):
        if game.game_over:
            game.end_game()
            break
        turn = player.take_turn(game)
        action = turn.action
        if action == "roll":
            game.roll_dice(player.name)
        elif action == "legbet":
            game.take_betting_tile(player.name, turn.color)
        elif action == "spectate":
            game.place_spectator_tile(player.name, turn.space_number, turn.cheering)
        elif action == "final":
            game.bet_final_bet(player.name, turn.color, turn.win)
