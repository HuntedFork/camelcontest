from brains.api import Brain, GameState, Roll, LegBet, Spectate, FinalBet

class RollBrain(Brain):
    def __init__(self, name="RollerDoger"):
        super().__init__(name)
    
    def take_turn(self, game: GameState):
        print(game.players[self.name].money)
        return Roll()