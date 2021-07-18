import sys
import berserk
import threading

def pretty(d, indent=0):
   for key, value in d.items():
      print('  ' * indent + str(key))
      if isinstance(value, dict):
         pretty(value, indent+1)
      else:
         print('  ' * (indent+1) + str(value))

LICHESS_TOKEN = ''
RESIGN_ONGOING_GAMES = True

session = berserk.TokenSession(LICHESS_TOKEN)
client = berserk.Client(session)

print('Starting script')

if RESIGN_ONGOING_GAMES:
  games = client.games.get_ongoing()
  for game in games:
    client.board.resign_game(game['gameId'])

# https://lichess.org/api#operation/challengeAi
challange = client.challenges.create_ai(
  level=1,
  clock_limit=15*60,
  clock_increment=15,
  color=berserk.enums.Color.BLACK
)

gameid = challange['id']

class GameEvents(threading.Thread):
  def __init__(self, gameid, **kwargs):
    super().__init__(**kwargs)
    self.gameid = gameid

  def run(self):
    for event in client.board.stream_game_state(self.gameid):
      pretty(event)

class GameControllers(threading.Thread):
  def __init__(self, gameid, **kwargs):
    super().__init__(**kwargs)
    self.gameid = gameid

  def run(self):
    while True:
      flagSuccess, moveSuccess, drawOfferSuccess = None, None, None
      move = input()
      try:
        if move == 'draw':
          drawOfferSuccess = client.board.offer_draw(self.gameid)
        elif move == 'flag':
          flagSuccess = client.board.resign_game(self.gameid)
        else:
          moveSuccess = client.board.make_move(self.gameid, move)
        if flagSuccess:
          print("Resign sent")
        if drawOfferSuccess:
          print("Draw offer sent")
        if moveSuccess:
          print("Move sent")
      except berserk.exceptions.ResponseError as response:
        print(response.cause['error'])
      except:
        raise e

events_listener, controllers = GameEvents(gameid), GameControllers(gameid)

events_listener.start()
controllers.start()
controllers.join()