import random
import copy

from flask.helpers import get_root_path, stream_with_context
class Game:
	def __init__(self, name):
		self.path = [44, 45, 46, 47, 48, 37, 26, 15, 4, 5, 6, 17, 28, 39, 50, 51, 52, 53, 54, 65, 76,
				75, 74, 73, 72, 83, 94, 105, 116, 115, 114, 103, 92, 81, 70, 69, 68, 67, 66, 55]
		self.name = name
		self.initSettings = {
			'turquoise': {
				'start': [12, 13, 23, 24],
				'epos': [56, 57, 58, 59],
				'path': self.path + [56, 57, 58, 59],
				'pathTokens': []
			},
			'golden': {
				'start': [89, 90, 100, 101],
				'epos': [104, 93, 82, 71],
				'path': self.path[-10:] + self.path[:-10] + [104, 93, 82, 71],
				'pathTokens': []
			},
			'crimson': {
				'start': [19, 20, 30, 31],
				'epos': [16, 27, 38, 49],
				'path': self.path[10:] + self.path[:10] + [16, 27, 38, 49],
				'pathTokens': []
			},
			'lime': {
				'start': [96, 97, 107, 108],
				'epos': [64, 63, 62, 61],
				'path': self.path[20:] + self.path[:20] + [64, 63, 62, 61],
				'pathTokens': []
			}
		}
		self.gameData = copy.deepcopy(self.initSettings)
		self.currentOptions = {}
		self.playerData = {}
		self.roomTsar = ""
		self.currentPlayer = 0
		self.roll = {}
		self.posMoves = []
		self.started = False
		self.hasAlreadyBeenRolled = False
		self.winner = False

	def rollDice(self):
		self.hasAlreadyBeenRolled = True
		x = random.randint(0, 5)
		if x == 4:
			x = 0
		elif x == 5:
			x = 2
		y = random.randint(0, 3)
		yArr = [1, 4, 2, 3]
		yArr2 = [2, 3, 1, 4]
		if x == 1:
			number = 6
		elif x == 3:
			number = 5
		elif x == 0:
			number = yArr[y]
		else:
			number = yArr2[y]
		return {'x': x, 'y': y, 'number': number}

	def get(self):
		return {'name': self.name, 'gameData': self.gameData, 'playerData': self.playerData, 'roomTsar': self.roomTsar, 'started': self.started, 'currentPlayer': self.currentPlayer}

	def getPossibleMoves(self):
		color = self.playerData[self.currentPlayer]['color']
		number = self.roll['number']
		res = {}
		data = self.gameData[color]
		#print("In getPosMov")
		#print("data:", data)
		if number == 1 or number == 6:
			self.posMoves += data['start']
			for token in data['start']:
				res[token] = data['path'][0]
		for token in data['pathTokens']:
			#print('Token, number: ', token, number)
			#print("if: ", len(data['path']) > token + number)
			#print(data['path'][token],':', data['path'][token + number])
			if len(data['path']) > token + number:
				if data['path'][token + number] in data['epos']:
					if token + number in data['pathTokens']:
						continue
				self.posMoves += [token]
				res[data['path'][token]] = data['path'][token + number]
		self.currentOptions = res
		#print('res:', res)
		return res

	def getPoints(self, color):
		res = 0
		for token in self.gameData[color]['pathTokens']:
			if token < 40:
				res += token + 1 + 10
			else:
				res += 50 + (token-39)*5
		return res

	def changeTurn(self):
		print(self.gameData)
		for color, data in self.gameData.items():
			if self.getPoints(color) == 250:
				self.winner = self.getPUUIDFromColor(color)
		playlist = [key for key in self.playerData.keys()]
		#print(playlist)
		self.currentPlayer = playlist[playlist.index(self.currentPlayer) + 1] if playlist.index(self.currentPlayer) < len(playlist)-1 else playlist[0]
		self.roll = {}
		self.hasAlreadyBeenRolled = False
		self.currentOptions = {}
		self.posMoves = []

	def getPUUIDFromColor(self, color):
		for key, value in self.playerData.items():
			if value['color'] == color:
				return value['pUUID']

	def getMoves(self):
		self.roll = self.rollDice()
		print(self.roll)
		self.posMoves = self.getPossibleMoves()
		print(self.posMoves)
		return {'diceData': self.roll, 'movesData': self.posMoves}

	def move(self, color, token):
		token = int(token) 
		if token not in self.gameData[color]['start']:
			token = self.gameData[color]['path'].index(token)
		smth = None
		print("InMove")
		print('Color, token: ', color, token)
		print('gameData[color]: ', self.gameData[color])
		print('check1: ', int(token) in self.gameData[color]['pathTokens'])
		print('check2: ', int(token) in self.gameData[color]['start'])
		if token in self.gameData[color]['pathTokens']:
			self.gameData[color]['pathTokens'].remove(token)
			self.gameData[color]['pathTokens']+=[token+self.roll['number']]
			smth = token+self.roll['number']
		elif token in self.gameData[color]['start']:
			self.gameData[color]['start'].remove(token)
			self.gameData[color]['pathTokens']+=[0]
			smth = 0
		self.checkForCollisions(self.gameData[color]['path'][smth], color)
		print('Current player: ', self.getCurrentPlayer)
		self.changeTurn()
		print('Current player: ', self.getCurrentPlayer)
		return {}

	def checkForCollisions(self, place, color):
		print(place, color)
		for key, value in self.gameData.items():
			if key != color:
				print('Oto tokeny: ', value['pathTokens'])
				toBeRemoved = []
				for token in value['pathTokens']:
					print('Oto token: ', token, value['path'][token])
					if value['path'][token] == place:
						toBeRemoved += [token]
						value['start'] += [random.choice([i for i in self.initSettings[key]['start'] if i not in value['start']])]
				for token in toBeRemoved:
					value['pathTokens'].remove(token)

	def start(self):
		self.gameData = copy.deepcopy(self.initSettings)
		self.started = True
		self.currentOptions = {}
		#print(list(self.playerData.keys()))
		self.currentPlayer = random.choice(list(self.playerData.keys()))
		self.roll = {}
		self.posMoves = []

	def addPlayer(self, data):
		if len(self.playerData) < 4:
			x = random.choice([x for x in [0, 1, 2, 3] if x not in self.playerData.keys()])
			self.playerData[x] = data
			self.playerData[x]['ping'] = 'N/A'
			if len(self.playerData) == 1:
				self.roomTsar = data['pUUID']

	def getColor(self, pUUID):
		for key, value in self.playerData.items():
			if value['pUUID'] == pUUID:
				return value['color']

	def removePlayer(self, pUUID):
		for key, value in self.playerData.items():
			if value['pUUID'] == pUUID:
				self.playerData.pop(key)
				#print(self.roomTsar, "\n", pUUID)
				if self.roomTsar == pUUID:
					#print(self.playerData)
					self.roomTsar = list(self.playerData.values())[0]['pUUID'] if len(self.playerData) > 0 else ""
				break

	def getCurrentPlayer(self, nick=None):
		#print("\n\nself.playerData: ", self.playerData, "\n\n")
		if nick is not None:
			return self.playerData[self.currentPlayer]['nick']
		else:
			return self.playerData[self.currentPlayer]['pUUID']

	def setLatency(self, pUUID, ping):
		for key, players in self.playerData.items():
			if players['pUUID'] == pUUID:
				players['ping'] = ping
				break