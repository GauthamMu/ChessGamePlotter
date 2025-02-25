# This program won't support processing multiple moves at once, and cetrainly not whole games or even PGN files.
# It also won't support inserting commentary.
# And yes, this includes writing "White resigns" or "Black resigns". Seriously, just write 1-0 or 0-1.
# This program intentionally does not support extra features like PGN parsing or commentary.
# However, it probably will be able to export the moves in PGN format.
# Also, this is no chess engine, so keep your long algebraics out of here, as this tool only supports moves up to 10 chars long.
# Wkr, GM

# Fancy intro message, probably not needed (Nvm it is, to get the user's language code)
languageCode = input(  # Language code feature will be implemented later, if at all. We'll start with English though.
		"""
	| a | b | c | d | e | f | g | h |
——+———+———+———+———+———+———+———+———+——
8 |   |   Welcome to the ...  |   | 8
——+———+———+———+———+———+———+———+———+——
7 |   |  Chess Game Plotter!  |   | 7
——+———+———+———+———+———+———+———+———+——
6 |   | Press Enter to start  |   | 6
——+———+———+———+———+———+———+———+———+——
5 |   |   Although, please    |   | 5
——+———+ include a two-letter —+———+——
4 |   | language code. (nvm don't)| 4
——+———+———+———+———+———+———+———+———+——
eg|EN = English   |DE = German    |eg
——+———+———+———+———+———+———+———+———+——
2 |    Otherwise, I'll assume |   | 2
——+—— you're english-speaking. ———+——
1 |   |   |   | Enjoy!    |   |   | 1
——+———+———+———+———+———+———+———+———+——
	| a | b | c | d | e | f | g | h |
""")

# Define how a chess piece looks, will probably be changed to use the chess piece emojis
# The variable names are shortened on purpose
bk = "BK"  # black king (\u2654)
bq = "BQ"  # black queen (\u2655)
br = "BR"  # black rook (\u2656)
bb = "BB"  # black bishop (\u2657)
bn = "BN"  # black knight (\u2658)
bp = "BP"  # black pawn (\u2659)
wk = "WK"  # white king (\u265A)
wq = "WQ"  # white queen (\u265B)
wr = "WR"  # white rook (\u265C)
wb = "WB"  # white bishop (\u265D)
wn = "WN"  # white knight (\u265E)
wp = "WP"  # white pawn (\u265F)
wSqr = "###"  # white chess board square (\u25A0)
bSqr = ""  # black chess board square

# These make it easier to determine if a capture is valid (to make sure you don't eat your own pieces)
blackPieces = [bk, bq, br, bb, bp]
whitePieces = [wk, wq, wr, wb, wp]
emptySqrs = [wSqr, bSqr]

chessBoard = [
	[br, bn, bb, bq, bk, bb, bn, br],
	[bp, bp, bp, bp, bp, bp, bp, bp],
	[wSqr, bSqr, wSqr, bSqr, wSqr, bSqr, wSqr, bSqr],
	[bSqr, wSqr, bSqr, wSqr, bSqr, wSqr, bSqr, wSqr],
	[wSqr, bSqr, wSqr, bSqr, wSqr, bSqr, wSqr, bSqr],
	[bSqr, wSqr, bSqr, wSqr, bSqr, wSqr, bSqr, wSqr],
	[wp, wp, wp, wp, wp, wp, wp, wp],
	[wr, wn, wb, wq, wk, wb, wn, wr]
]

# Important variables used later on
check = False
doubleCheck = False
checkmate = False
kingMoved = [False, False]  # Important for castling
kingsRookMoved = [False, False]  # Important for castling
queensRookMoved = [False, False]  # Important for castling
piecesBlackCaptured = []
piecesWhiteCaptured = []
enPassentSqr = ""  # Important when implementing en passent

fileToIndex = {
	"a": 0,
	"b": 1,
	"c": 2,
	"d": 3,
	"e": 4,
	"f": 5,
	"g": 6,
	"h": 7
}

# To print the current chess board


def printChessBoard():
	print("Current chess board:")
	if piecesBlackCaptured:
		# Prints piecesBlackCaptured, with a space as seperator, if it's not empty
		print(" ".join(piecesBlackCaptured))
	print("  | a | b | c | d | e | f | g | h |")
	rank = 8
	for i in chessBoard:
		print(f"——+———+———+———+———+———+———+———+———+——\n{rank} |", end="")
		for j in i:
			print(j.ljust(3), end="|")
		print(f" {rank}")
		rank -= 1
	print("——+———+———+———+———+———+———+———+———+——\n  | a | b | c | d | e | f | g | h |")
	if piecesWhiteCaptured:
		# Prints piecesWhiteCaptured, with a space as seperator, if it's not empty
		print(" ".join(piecesWhiteCaptured))


# To validate the chess square part of the input
possibleChessSquareCharacters = ["a", "b", "c", "d", "e", "f", "g", "h", "1", "2",
																 "3", "4", "5", "6", "7", "8", "K", "Q", "B", "N", "R"]  # Includes piece letters


def chessSquareValidation(square):
	if len(square) != 2:  # Validates the length of the chess square to 2 digits, returns early if length isn't correct
		return "not right length"

	for i in square:
		# Returns early if the chess square contains characters outside of a-h, 1-8
		if i not in possibleChessSquareCharacters:
			return "invalid chess square"

	file, rank = square[0], square[1]
	if file.isalpha() and rank.isdigit():  # Returns this if chess square is letter and digit (normal)
		return "normal chess square"
	elif file.isalpha() and rank.isalpha():  # Returns this if chess square is letter and letter (pawn capture)
		# Detects if the files are adjacent
		if ord(file) == ord(rank) + 1 or 1 + ord(file) == ord(rank):
			return "pawn capture"  # And therefore if a pawn capture is posssible
		else:  # Returns "invalid pawn capture otherwise"
			return "invalid pawn capture"
	elif file.isdigit() and rank.isalpha():  # Returns this if chess square is digit and letter (reverse of normal)
		return "reverse chess square"
	else:  # Returns this if chess square is two digits (ICCF notation)
		return "iccf notation chess square"

# Function to clear square, remove piece from it, should called after every piece move


def clearSquare(rank, file):
	if (rank + file) % 2 == 0:  # Calls if white square is needed
		chessBoard[rank][file] = wSqr
	else:  # Calls if black square is needed
		chessBoard[rank][file] = bSqr


def pawnMoveValidation(move):
	if len(move) == 2:
		typeOfSquare = chessSquareValidation(move)
		# Gets called if square coordinates are files which are not next to each other
		if typeOfSquare == "invalid pawn capture":
			print("Invalid move. Please use algebraic notation.")
			return "invalid"
		elif typeOfSquare == "normal chess square":
			if currentTurn == "w":  # Current player is white
				# Fires when white attempts to move pawn backwards or sideways with a pawn
				if move[1] in ["1", "2"]:
					print(
							"You can't move your pawn backwards or sideways. Use algebraic notation.")
					return "invalid"
				else:
					# Not a regular capture
					if chessBoard[8 - int(move[1])][fileToIndex[move[0]]] in [wSqr, bSqr]:
						# Checking if the square in front of the desired square is a white pawn, which it is unless initial two-square advance
						if chessBoard[9 - int(move[1])][fileToIndex[move[0]]] == wp:
							# Using the new executeMove function
							executeMove(
									[9 - int(move[1]), fileToIndex[move[0]]], [8 - int(move[1]), fileToIndex[move[0]]])
						# Checking if initial two-square advance
						elif move[1] == "4" and chessBoard[6][fileToIndex[move[0]]] == wp and chessBoard[5][fileToIndex[move[0]]] in [wSqr, bSqr]:
							# Using the new executeMove function
							executeMove([6, fileToIndex[move[0]]],
													[4, fileToIndex[move[0]]])
					else:  # A regular capture
						pass
			else:  # Current player is black
				# Fires when black attempts to move pawn backwards or sideways with a pawn
				if move[1] in ["7", "8"]:
					print(
							"You can't move your pawn backwards or sideways. Use algebraic notation.")
					return "invalid"
				else:
					# Not a regular capture
					if chessBoard[8 - int(move[1])][fileToIndex[move[0]]] in [wSqr, bSqr]:
						# Checking if the square in front of the desired square is a black pawn, which it is unless initial two-square advance
						if chessBoard[7 - int(move[1])][fileToIndex[move[0]]] == bp:
							chessBoard[8 - int(move[1])][fileToIndex[move[0]]] = chessBoard[7 - int(
									# Moving pawn to the desired square
									move[1])][fileToIndex[move[0]]]
							# Clears initial pawn position
							clearSquare(7 - int(move[1]), fileToIndex[move[0]])
						# Checking if initial two-square advance
						elif move[1] == "5" and chessBoard[1][fileToIndex[move[0]]] == bp and chessBoard[2][fileToIndex[move[0]]] in [wSqr, bSqr]:
							# Moving pawn to the desired square
							chessBoard[3][fileToIndex[move[0]]
														] = chessBoard[1][fileToIndex[move[0]]]
							# Clears initial pawn position
							clearSquare(1, fileToIndex[move[0]])
					else:  # A regular pawn capture
						pass
		elif typeOfSquare == "pawn capture":
			if currentTurn == "w":  # Current player is white
				for i, rank in list(enumerate(chessBoard))[1:6]:
					if rank[fileToIndex[move[0]]] == wp and chessBoard[i - 1][fileToIndex[move[1]]] in blackPieces:
						possibleOriginSquares.append([i, fileToIndex[move[0]]])

				if len(possibleOriginSquares) == 1:
					executeMove(possibleOriginSquares[0], [
											possibleOriginSquares[0][0] - 1, fileToIndex[move[1]]])
				elif len(possibleOriginSquares) == 2:
					print(
							"I didn't implement being able to choose between two different pawns yet")
			else:  # Current player is black
				for i, rank in list(enumerate(chessBoard))[2:7]:
					if rank[fileToIndex[move[0]]] == bp and chessBoard[i + 1][fileToIndex[move[1]]] in whitePieces:
						possibleOriginSquares.append([i, fileToIndex[move[0]]])

				if len(possibleOriginSquares) == 1:
					executeMove(possibleOriginSquares[0], [
											possibleOriginSquares[0][0] + 1, fileToIndex[move[1]]])
				elif len(possibleOriginSquares) == 2:
					print(
							"I didn't implement being able to choose between two different pawns yet")
	elif len(move) == 3:
		if move[0] == "x":  # Pawn capture
			typeOfSquare = chessSquareValidation(move[1:])
			if typeOfSquare == "normal chess square":
				if currentTurn == "w":  # Current player is white
					# Fires when white attempts to capture piece backwards or sideways with a pawn
					if move[1] in ["1", "2"]:
						print(
								"You can't capture with your pawn backwards or sideways. Use algebraic notation.")
						return "invalid"
					else:
						# A regular capture
						if chessBoard[8 - int(move[2])][fileToIndex[move[1]]] in blackPieces:
							if move[1] != "a":
								if chessBoard[9 - int(move[2])][fileToIndex[move[1]] - 1] == wp:
									possibleOriginSquares.append(
											[9 - int(move[2]), fileToIndex[move[1]] - 1])
							if move[1] != "h":
								if chessBoard[9 - int(move[2])][fileToIndex[move[1]] + 1] == wp:
									possibleOriginSquares.append(
											[9 - int(move[2]), fileToIndex[move[1]] + 1])
							if len(possibleOriginSquares) == 1:
								executeMove(possibleOriginSquares[0], [
														8 - int(move[2]), fileToIndex[move[1]]])
							elif len(possibleOriginSquares) == 2:
								print(
										"I didn't implement being able to choose between two different pawns yet")
						# En passant capture
						elif chessBoard[8 - int(move[2])][fileToIndex[move[1]]] in emptySqrs:
							pass
						else:
							print(
									"You can't eat your own pieces with your own pawn.")
							return "invalid"
				else:  # Current player is black
					# Fires when black attempts to capture piece backwards or sideways with a pawn
					if move[1] in ["7", "8"]:
						print(
								"You can't capture with your pawn backwards or sideways. Use algebraic notation.")
						return "invalid"
					else:
						# A regular capture
						if chessBoard[8 - int(move[2])][fileToIndex[move[1]]] in whitePieces:
							if move[1] != "a":
								if chessBoard[7 - int(move[2])][fileToIndex[move[1]] - 1] == bp:
									possibleOriginSquares.append(
											[7 - int(move[2]), fileToIndex[move[1]] - 1])
							if move[1] != "h":
								if chessBoard[7 - int(move[2])][fileToIndex[move[1]] + 1] == bp:
									possibleOriginSquares.append(
											[7 - int(move[2]), fileToIndex[move[1]] + 1])
							if len(possibleOriginSquares) == 1:
								executeMove(possibleOriginSquares[0], [
														8 - int(move[2]), fileToIndex[move[1]]])
							elif len(possibleOriginSquares) == 2:
								print(
										"I didn't implement being able to choose between two different pawns yet")
						# En passant capture
						elif chessBoard[8 - int(move[1])][fileToIndex[move[0]]] in emptySqrs:
							pass
						else:
							print(
									"You can't eat your own pieces with your own pawn.")
							return "invalid"
	elif len(move) == 4:  # Pawn capture with check
		pass
	elif len(move) == 5:  # Pawn promotion with capture or check
		pass
	elif len(move) == 5:  # Pawn promotion with capture and check
		pass


def rookMoveValidation(move):
	if len(move) == 3:
		pass
	elif len(move) == 4:
		pass
	elif len(move) == 5:
		pass


def bishopMoveValidation(move):
	if len(move) == 3:
		pass
	elif len(move) == 4:
		pass
	elif len(move) == 5:
		pass


# Function to convert algebraic notation to "board notation" (my chess game's internally used notation, to access the pieces)
def aM2bM(move, fileMod=0, rankMod=0):
	if len(move) != 2:
		print("move not the right length (function aM2bM, line 257)")
	return [8 - int(move[1]) + rankMod, fileToIndex[move[0]] + fileMod]


def knightTheoreticalMoves(move):
	move = move[1:]
	allMoves = [aM2bM(move, 1, 2), aM2bM(move, 2, 1), aM2bM(move, -1, 2), aM2bM(move, -2, 1),
							aM2bM(move, 1, -2), aM2bM(move, 2, -1), aM2bM(move, -1, -2), aM2bM(move, -2, -1)]
	theoreticalMoves = []
	for Move in allMoves:
		if 0 <= Move[0] and Move[0] < 8:
			if 0 <= Move[1] and Move[1] < 8:
				theoreticalMoves.append(Move)
	print("theoreticalMoves:", theoreticalMoves)
	return theoreticalMoves


def knightPossibleMoves(move):
	# Knight's Theoretical Moves (taking chess board borders into consideration, but not locations of own knights)
	kTM = knightTheoreticalMoves(move)
	# List for Knight's Possible Moves (taking locations of own knights into consideration)
	kPM = []

	if currentTurn == "w":
		for Move in kTM:
			if chessBoard[Move[0]][Move[1]] == wn:
				kPM.append(Move)
	else:
		for Move in kTM:
			if chessBoard[Move[0]][Move[1]] == bn:
				kPM.append(Move)
	print("possibleMoves:", kPM)
	return kPM


def knightMoveValidation(move):
	if len(move) == 3:
		typeOfSquare = chessSquareValidation(move[1:])
		if typeOfSquare == "normal chess square":
			possibleOriginSquares = knightPossibleMoves(move)
			if len(possibleOriginSquares) == 1:
				executeMove(possibleOriginSquares[0], aM2bM(move[1:]))
			elif len(possibleChessSquareCharacters) >= 2:
				print(
						"I haven't implemented selecting between multiple Knights yet (knightMoveValidation, line 295)")
	elif len(move) == 4:
		if move[1] == "x":
			typeOfSquare = chessSquareValidation(move[2:])
			if typeOfSquare == "normal chess square":
				move = move.replace("x", "")
				possibleOriginSquares = knightPossibleMoves(move)
				if len(possibleOriginSquares) == 1:
					executeMove(possibleOriginSquares[0], aM2bM(move[1:]))
				elif len(possibleChessSquareCharacters) >= 2:
					print(
							"I haven't implemented selecting between multiple Knights yet (knightMoveValidation, line 305)")
	elif len(move) == 5:
		pass


def queenMoveValidation(move):
	if len(move) == 3:
		pass
	elif len(move) == 4:
		pass
	elif len(move) == 5:
		pass


def kingMoveValidation(move):
	if len(move) == 3:
		pass
	elif len(move) == 4:
		pass
	elif len(move) == 5:
		pass


# Will be useful when tackling pawn captures and piece moves, which can happen from multiple squares, unlike regular pawn moves
possibleOriginSquares = []

# To validate the input as a whole


def moveValidation(move):
	if len(move) < 2:  # Return early if move is too short
		print("Your move is too short. Please use regular algebraic notation.")
		return "too short"
	elif len(move) > 10:  # Return early (with some helpful tips) if move is too long
		print("Your move is too long. Please use regular algebraic notation without any extras, please. \n \
							Please use + for checks, regardless of what kind, and # for checkmates, also regardless of what kind.")
		return "too long"

	if len(move) == 2:  # Validate if the move is a valid chess square if it is 2 characters long (only fits a square, therefore a pawn move)
		pawnMoveValidation(move)
	elif len(move) == 3:  # piece move (Nf3), pawn capture (xd5), pawn check (d6+), pawn mate (g5#) or kingside castling (0-0)
		if move[0] in ["N", "B", "R", "Q", "K"]:  # Possible pieces
			if move[0] == "R":
				rookMoveValidation(move)
			elif move[0] == "B":
				bishopMoveValidation(move)
			elif move[0] == "N":
				knightMoveValidation(move)
			elif move[0] == "Q":
				queenMoveValidation(move)
			elif move[0] == "K":
				kingMoveValidation(move)
		elif move[0] == "x" or move[2] in ["+", "#"]:
			pawnMoveValidation(move)
	elif len(move) == 4:  # capture (Nxe5), check (Qe2+), checkmate (Qg7#) and ICCF notation (5254)
		if move[0] in ["N", "B", "R", "Q", "K"]:  # Possible pieces
			if move[0] == "R":
				rookMoveValidation(move)
			elif move[0] == "B":
				bishopMoveValidation(move)
			elif move[0] == "N":
				print("knight move sent to knightMoveValidation")
				knightMoveValidation(move)
			elif move[0] == "Q":
				queenMoveValidation(move)
			elif move[0] == "K":
				kingMoveValidation(move)
	elif len(move) == 5:  # queenside castling (0-0-0), ICCF pawn promotion (47481) check with capture (Rxb1+) or checkmate with capture (Rdxe1#)
		pass
	elif len(move) == 6:
		pass
	elif len(move) == 7:
		pass
	elif len(move) == 8:
		pass
	elif len(move) == 9:
		pass
	elif len(move) == 10:
		pass


def executeMove(originSqr, destinationSqr):  # Function for actually moving the pieces
	if len(originSqr) == 2 and len(destinationSqr) == 2:
		if chessBoard[destinationSqr[0]][destinationSqr[1]] not in emptySqrs:
			if chessBoard[destinationSqr[0]][destinationSqr[1]] in whitePieces:
				piecesBlackCaptured.append(
						chessBoard[destinationSqr[0]][destinationSqr[1]])
			else:
				piecesWhiteCaptured.append(
						chessBoard[destinationSqr[0]][destinationSqr[1]])
		# Moving pawn to the desired square
		chessBoard[destinationSqr[0]][destinationSqr[1]
																	] = chessBoard[originSqr[0]][originSqr[1]]
		clearSquare(originSqr[0], originSqr[1])  # Clears initial pawn position
	else:
		print("Something went wrong (lists provided in executeMove were too long or short)")
		print("originSqr:", originSqr)
		print("destinationSqr:", destinationSqr)


printChessBoard()


def switchCurrentPlayer(currentTurn):
	if currentTurn == "w":
		return ["b", "black"]
	else:
		return ["w", "white"]


currentTurn = "b"

while True:  # Loop for chess game
	currentTurn, currentTurnL = switchCurrentPlayer(
			currentTurn)  # Switches current turn
	# Strip to remove leading and trailing whitespace
	move = input(f"Enter {currentTurnL} move: ").strip()
	moveValidation(move)  # Runs move through the move validation
	printChessBoard()
	possibleOriginSquares = []  # Resets possibleOriginSquares to empty list
