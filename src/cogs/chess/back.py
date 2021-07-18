import berserk
import json

"""
move response:
"""

LICHESS_TOKEN = ''

session = berserk.TokenSession(LICHESS_TOKEN)
client = berserk.Client(session)

print('Starting scripts')

acc = client.account.get()

print(acc)

# https://lichess.org/api#operation/challengeAi
challange = client.challenges.create_ai(
  level=1,
  clock_limit=15*60,
  clock_increment=15,
  color=berserk.enums.Color.BLACK
)

gameid = challange['id']

for event in client.board.stream_game_state(gameid):
  print("### EVENT ###")
  print(event)
  if 'state' not in  event:
    raise Exception("state not in event")
  state = event['state']
  if state['type'] == 'gameState':
    print(f"AI played {state['moves']}\n White time {state['wtime']}\nBlack time {state['btime']}")
  move = input()
  client.board.make_move(gameid, move.strip('\n'))
