import sys
import berserk
import threading

from .exceptions import InvalidMove, InvalidPosition
from enum import Enum

class Pieces():
  NONE = ' '
  WHITE_KING = '\u2654'
  WHITE_QUEEN = '\u2655'
  WHITE_ROOK = '\u2656'
  WHITE_BISHOP = '\u2657'
  WHITE_KNIGHT = '\u2658'
  WHITE_PAWN = '\u2659'
  BLACK_KING = '\u265A'
  BLACK_QUEEN = '\u265B'
  BLACK_ROOK = '\u265C'
  BLACK_BISHOP = '\u265D'
  BLACK_KNIGHT = '\u265E'
  BLACK_PAWN = '\u265F'

def createBoard():
  """ Creates matrix[8][8]:
    matrix[i][j] gets the i'th line and j'th column piece
  """
  return [
    [ Pieces.WHITE_ROOK, Pieces.WHITE_KNIGHT, Pieces.WHITE_BISHOP, Pieces.WHITE_QUEEN, Pieces.WHITE_KING, Pieces.WHITE_BISHOP, Pieces.WHITE_KNIGHT, Pieces.WHITE_ROOK],
    [ Pieces.WHITE_PAWN, Pieces.WHITE_PAWN, Pieces.WHITE_PAWN, Pieces.WHITE_PAWN, Pieces.WHITE_PAWN, Pieces.WHITE_PAWN, Pieces.WHITE_PAWN, Pieces.WHITE_PAWN ],
    [ Pieces.NONE, Pieces.NONE, Pieces.NONE, Pieces.NONE, Pieces.NONE, Pieces.NONE, Pieces.NONE, Pieces.NONE ],
    [ Pieces.NONE, Pieces.NONE, Pieces.NONE, Pieces.NONE, Pieces.NONE, Pieces.NONE, Pieces.NONE, Pieces.NONE ],
    [ Pieces.NONE, Pieces.NONE, Pieces.NONE, Pieces.NONE, Pieces.NONE, Pieces.NONE, Pieces.NONE, Pieces.NONE ],
    [ Pieces.NONE, Pieces.NONE, Pieces.NONE, Pieces.NONE, Pieces.NONE, Pieces.NONE, Pieces.NONE, Pieces.NONE ],
    [ Pieces.BLACK_PAWN, Pieces.BLACK_PAWN, Pieces.BLACK_PAWN, Pieces.BLACK_PAWN, Pieces.BLACK_PAWN, Pieces.BLACK_PAWN, Pieces.BLACK_PAWN, Pieces.BLACK_PAWN],
    [ Pieces.BLACK_ROOK, Pieces.BLACK_KNIGHT, Pieces.BLACK_BISHOP, Pieces.BLACK_QUEEN, Pieces.BLACK_KING, Pieces.BLACK_BISHOP, Pieces.BLACK_KNIGHT, Pieces.BLACK_ROOK]
  ]

def position_to_index(position):
  column, line = position
  col_index = ord(column) - ord('a')
  row_index = ord(line) - ord('1')  
  if not (0 <= row_index < 8) or not (0 <= col_index < 8):
    raise InvalidPosition(f'{position} is not a valid position')
  return row_index, col_index

def getPiece(board, position):
  row_index, col_index = position_to_index(position)
  return board[row_index][col_index]

def setPiece(board, position, piece):
  row_index, col_index = position_to_index(position)
  board[row_index][col_index] = piece
  return board

def movesToBoard(moves):
  board = createBoard()
  for move in moves:
    frompos, topos = move[0:2], move[2:]
    piece = getPiece(board, frompos)
    if piece is Pieces.NONE:
      raise InvalidMove(f"No piece in {frompos}")
    setPiece(board, frompos, Pieces.NONE)
    setPiece(board, topos, piece)
  return board


def rowindexstring(index, show):
  if show:
    return f" - {index+1}"
  return ''

def rowToString(rowindex, row):
  def f(i, p):
    return f"[{str(p)}]{rowindexstring(rowindex, i == 7)}"
  return "".join([
    f(i, p) for i, p in enumerate(row)
  ])

def boardToString(board):
  not_indexed_board = "\n".join(
    [ rowToString(i, r) for i, r in enumerate(board)]
  )
  bottom_index = "\n A  B  C  D  E  F  G  H "
  return  not_indexed_board + bottom_index
  
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
  print('Resigning all on going games')
  games = client.games.get_ongoing()
  for game in games:
    client.board.resign_game(game['gameId'])
  print('resigned all games')

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
      state = None
      if event['type'] == 'gameFull':
        state = event['state']
      elif event['type'] == 'gameState':
        state = event
      else:
        raise Exception(f"Unknown event type {event['type']}")
      board = movesToBoard(state['moves'].split(' '))
      boardStr = boardToString(board)
      print(boardStr)

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