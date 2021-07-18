import random

from discord.ext.commands import Cog, command

class ChessBot(Cog):
    def __init__(self, bot):
        self.bot = bot
        self.games = {} # maps discord user id to game (??? whatever it is)

    @command()
    def chess(self, ctx):
        """
        $chess black        ->  starts a new game against akira as black
        $chess white        ->  same as above but as whites
        $chess              ->  same as above but random color
            all above subcommands can throw AlreadyPlayingException
        $chess <move>       ->  plays a move in a on-going game
            can throw InvalidMoveException
            can throw WaitYourTurnException
        $chess surrender    -> surrender your game against akira
            can throw WaitYourTurnException
        $chess draw         -> propose a draw
            can throw WaitYourTurnException
        $chess flipboard    -> rage quit. you loose
        $chess difficulty N -> sets the difficulty
        """
        pass

