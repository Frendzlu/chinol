#$env:FLASK_ENV = "development"
from flask import Flask, render_template, request, Response, redirect, url_for, json, abort
import uuid
import mimetypes
import random
import time
import math
from game import Game
from datetime import datetime
mimetypes.init()
mimetypes.add_type('application/javascript', '.mjs')
mimetypes.add_type('application/javascript', '.js')
mimetypes.add_type('text/css', '.css')
app = Flask(__name__) 

rooms = {
    "roomsOpen": {
        "roomsIdle": {}, 
        "roomsOngoing": {}
    },
    "roomsFull" : {}
}
peopleOnline = {}
roomNames = []
dynamicRooms = []
forbiddenNames = []
@app.route("/")
def hmm():
    mimetypes.add_type('application/javascript', '.mjs')
    mimetypes.add_type('application/javascript', '.js')
    mimetypes.add_type('text/css', '.css')
    if request.cookies.get('pUUID') in peopleOnline.keys():
        x = checkForGame(request.cookies.get('pUUID'))
        if x:
            return redirect('/room/{}'.format(x))
        else:
            return redirect(url_for('lis'))
    return render_template('nickQuestion.html', redirect='/list')

@app.route("/list", methods=["GET", "POST"])
def lis():
    if request.cookies.get('pUUID') in peopleOnline.keys():
        x = checkForGame(request.cookies.get('pUUID'))
        if x:
            return redirect('/room/{}'.format(x))
    return render_template('roomList.html', data=rooms['roomsOpen'])

@app.route("/listUpdate", methods=["POST"])
def updateList():
    return {"data": rooms['roomsOpen']}

@app.route('/room/<path:roomID>/gameData', methods=['POST'])
def update(roomID):
    #print ('\ninUpdate-RoomID: {}\n'.format(roomID))
    response = redirect(url_for('lis'))
    x = checkForGame(request.cookies.get('pUUID'))
    if x:
        if x == roomID:
            latestRequest = math.ceil(time.time()*1000)
             
            data = json.loads(request.data)
            #print ('\ninUpdate-RoomID: {}\n'.format(roomID))
            room = searchForRoom(roomID)
            #F(room)
            if latestRequest >= room['nextTurn'] and room['nextTurn']:
                room['gameData'].changeTurn()
                room['nextTurn'] = latestRequest+30000
            gameData = room['gameData'].get()
            latency = latestRequest - data['time']
            room['gameData'].setLatency(request.cookies.get('pUUID'), latency)
            room['playerNetworkInfo'][request.cookies.get('pUUID')] = latestRequest
            toLeave = []
            for key, value in room['playerNetworkInfo'].items():
                #print ("value: ", value, ', latestRequest: ', latestRequest-15000)
                if int(value) < latestRequest-15000:
                    toLeave.append([x, key])
            for leaving in toLeave:
                leave(leaving[0], leaving[1])
            #print(gameData['playerData'].items())
            gameDataFiltered = [{'color': key, 'values': value['start']+[value['path'][el] for el in value['pathTokens']]} for key, value in gameData['gameData'].items()]
            playerDataFiltered = [{'name': value['nick'], 'color': value['color'], 'score': room['gameData'].getPoints(value['color']), 'ping': value['ping']} for key, value in gameData['playerData'].items()]
            #print(gameDataFiltered)
            #print(playerDataFiltered)
            isMyTurn = request.cookies.get('pUUID') == room['gameData'].getCurrentPlayer() if gameData['started'] else False
            response = {
                'winner': peopleOnline[room['gameData'].winner]['nick'] if room['gameData'].winner else False,
                'private': room['private'],
                'playerData':  playerDataFiltered,
                'gameData': gameDataFiltered,
                'roomTsar': peopleOnline[gameData['roomTsar']],
                'playersReady': [peopleOnline[pUUID]['nick'] for pUUID in room['ready']],
                'started': gameData['started'],
                'amIroomTsar': request.cookies.get('pUUID') == gameData['roomTsar'],
                'isMyTurn': isMyTurn,
                'whoseTurn': room['gameData'].getCurrentPlayer(True) if gameData['started'] else False,
                'hasAlreadyBeenRolled': room['gameData'].hasAlreadyBeenRolled,
                'nextTurn': room['nextTurn']
            }
            if isMyTurn and room['gameData'].hasAlreadyBeenRolled:
                response['moveData'] = {'diceData': room['gameData'].roll, 'movesData': room['gameData'].posMoves}
            else:
                response['moveData'] = False
            #print('Pre-response: ', response)
    return response

@app.route('/room/<roomName>', methods=['GET'])
def joinRoom(roomName):
    global dynamicRooms
    #print('\ninRoom-dynamicRooms: ', dynamicRooms)
    #print(roomNames)
    #print(peopleOnline)
    if roomName in roomNames:
        #print(1)
        if roomName in rooms['roomsFull'].keys():
            if request.method == 'GET':
                abort(403, 'The room you tried to join is already full!') #roomfull
        #print(2)
        #print (request.cookies, "\n", peopleOnline.keys())
        if request.cookies.get('pUUID') not in peopleOnline.keys():
            return render_template('nickQuestion.html')
        #print(3)
        x = checkForGame(request.cookies.get('pUUID'))
        if x:
            if x == roomName:
                return render_template('gameUI.html')
            leave(x, request.cookies.get('pUUID'))
        #print(4)
        if roomName in rooms['roomsOpen']['roomsIdle'].keys():
            path = 'roomsIdle'
            #print(rooms)
            room = rooms['roomsOpen']['roomsIdle'][roomName]
        else:
            path = 'roomsOngoing'
            #print(rooms)
            room = rooms['roomsOpen']['roomsOngoing'][roomName]
        #print(5, "\n", room)
        color = random.choice(room['colorsLeft'])
        room['gameData'].addPlayer({
            'pUUID': request.cookies.get('pUUID'),
            'nick': request.cookies.get('pNICK'),
            'color': color
        })
        peopleOnline[request.cookies.get('pUUID')]['game'] = roomName
        room['colorsLeft'].remove(color)
        #print(6)
        if len(room['colorsLeft']) == 0:
            room['gameData'].started = True
            rooms['roomsFull'][roomName] = room
            rooms['roomsOpen'][path].pop(roomName)
            if roomName in dynamicRooms:
                dynamicRooms.remove(roomName)
        #print(7)
        #print(rooms)
        #print(room)
        return render_template('gameUI.html')
    else:
        abort(404, 'The room you tried to join does not exist!') #roomNotExists

@app.route('/randomOngoing', methods=['POST'])
def joinRandom():
    roomArr = rooms['roomsOpen']['roomsOngoing'].items()
    #print('inRandomOngoing-roomArr: ', roomArr)
    roomsFiltered = [roomName for roomName, roomData in roomArr if not roomData['private']]
    #print('inRandomOngoing-roomsFiltered: ',roomsFiltered)
    if len(roomsFiltered) != 0:
        x = random.choice(roomsFiltered)
        return {'redirect': '/room/{}'.format(x[0])}
    else:
        return {'error': 'No ongoing rooms found!'}

@app.route('/join', methods=['POST'])
def join():
    if len(dynamicRooms) != 0:
        return {'redirect': '/room/{}'.format(random.choice(dynamicRooms))}
    else:
        return makeroom()

@app.route('/makeroom', methods=['POST'])
def makeroom():
    randName = generateRandomName(5)
    while randName in roomNames:
        randName = generateRandomName(5)
    roomNames.append(randName)
    rooms['roomsOpen']['roomsIdle'][randName] = {
        "private": False,
        "gameData": Game(randName),
        "colorsLeft": ['turquoise', 'golden', 'crimson', 'lime'],
        'playerNetworkInfo': {},
        'ready': [],
        'latestRoll': {
            'value': '',
            'pUUID': '',
            'time': ''
        },
        'nextTurn': False
    }
    global dynamicRooms
    dynamicRooms += [randName]
    return {'redirect': '/room/{}'.format(randName)}

@app.route('/setnick', methods=['POST'])
def setnick():
    data = json.loads(request.data)
    global forbiddenNames
    #print(data['nick'])
    #print(forbiddenNames)
    if data['nick'] in forbiddenNames:
        return {'redirect': (url_for('abortMe'))}
    else:
        #print('\n\ninSetnick-data:', data, '\n\n')
        playerUUID = str(uuid.uuid4())
        nick =  data['nick'] if data['nick'] != "" else "guest-" + generateRandomName(5)
        peopleOnline[playerUUID] = {
            "nick": nick,
            "game": ""
        }
        #print ('\n\ninSetnick-playerUUID:', playerUUID, '\n\n')
    return {"pUUID": playerUUID, 'nick': nick, 'redirect': data['calee']}

def generateRandomName(length):
	chars = '1234567890poiuytrewqasdfghjklmnbvcxz'
	res = ""
	for letter in range(length):
		res += chars[random.randint(0, len(chars)-1)]
	return res

def checkForGame(player):
    if peopleOnline[player]['game'] != "":
        return peopleOnline[player]['game']
    else:
        return False

@app.errorhandler(404)
def page_not_found(error):
   return render_template('error.html', title = '404', error=error, url=url_for('lis')), 404

@app.route('/y_tho')
def abortMe():
    abort(418)

@app.errorhandler(418)
def jeste_czajniczkiem(error):
    return render_template('error.html', title = '418', error=error, url=url_for('lis'), image='teapot.png', body='The requested entity body is shot and stout'), 418

@app.errorhandler(403)
def page_not_found(error):
   return render_template('error.html', title = '403', error=error, url=url_for('lis')), 403

@app.route('/room/<x>/leave/<pUUID>', methods=['GET'])
def leave(x, pUUID):
    peopleOnline[pUUID]['game'] = ""
    room = searchForRoom(x)
    color = room['gameData'].getColor(pUUID)
    room['gameData'].removePlayer(pUUID)
    if pUUID in room['ready']:
        room['ready'].remove(pUUID)
    #print("\n\ncolorsLeft: ", room['colorsLeft'], "; colorAdded: ", color)
    room['colorsLeft'] += [color]
    room['playerNetworkInfo'].pop(pUUID)
    checkForEmptyness(x)
    return {'redirect': url_for('lis')}

@app.route('/makeMove', methods=['POST'])
def makeMove():
    pUUID = request.cookies.get('pUUID')
    x = peopleOnline[pUUID]['game']
    if x:
        room = searchForRoom(x)
        if room:
            if pUUID == room['gameData'].getCurrentPlayer():
                data = json.loads(request.data)
                #print(data)
                room['gameData'].move(room['gameData'].getColor(pUUID), data['chosenTile'])
                room['nextTurn'] = math.ceil(time.time()*1000)+30000
        return {}
    else:
        return {'msg': 'unable'}

@app.route('/rollDice', methods=['POST'])
def rollDice():
    x = peopleOnline[request.cookies.get('pUUID')]['game']
    room = searchForRoom(x)
    if request.cookies.get('pUUID') == room['gameData'].getCurrentPlayer():
        if room['gameData'].hasAlreadyBeenRolled:
            return {'error': 'AlreadyRolled!'}
        data = room['gameData'].getMoves()
        if len(data['movesData']) == 0:
            room['gameData'].changeTurn()
            room['nextTurn'] = math.ceil(time.time()*1000)+30000
        #print('\n\n\n\n========================MOVEDATA======================', data, "\n\n\n\n")
        #moveData = room['gameData'].getPossibleMoves()
        return {'moveData': data}
    else:
        return {'error': 'cheater'}

    
@app.route('/setPrivate', methods=['POST'])
def setPrivate():
    global dynamicRooms
    #print(dynamicRooms)
    x = peopleOnline[request.cookies.get('pUUID')]['game']
    room = searchForRoom(x)
    #print('===== ROOM ====\n\t', room,)
    if request.cookies.get('pUUID') == room['gameData'].roomTsar:
        #print('===== DATA ====\n\troom: ', room, "\n\tx: ", x, "\n\tdynamicRooms: ", dynamicRooms, "\n\troomPriv: ", room['private'])
        if x in dynamicRooms:
            dynamicRooms.remove(x)
            room['private'] = True
        else:
            dynamicRooms += [x]
            room['private'] = False
        return {'msg': 'setprivate'}
    else:
        return {'error': 'You do not have the permission!'}

@app.route('/ready', methods=['POST'])
def setReadiness():
    pUUID = request.cookies.get('pUUID')
    if pUUID in peopleOnline.keys():
        x = peopleOnline[pUUID]['game']
        room = searchForRoom(x)
        #print('setReadiness')
        #print(room)
        #print(room['gameData'].get())
        if not room['gameData'].get()['started']: 
            if pUUID in room['ready']:
                room['ready'].remove(pUUID)
            else:
                room['ready'] += [pUUID]
            if len(room['ready']) > 1:
                #print('it is')
                room['gameData'].start()
                room['nextTurn'] = math.ceil(time.time()*1000) + 30000
            return {'resp': pUUID in room['ready']}
        else:
            return
    else:
        return
    
def searchForRoom(room):
    if room in roomNames:
        if room in rooms['roomsOpen']['roomsIdle'].keys():
            roomObj = rooms['roomsOpen']['roomsIdle'][room]
        elif room in rooms['roomsOpen']['roomsOngoing'].keys():
            roomObj = rooms['roomsOpen']['roomsOngoing'][room]
        elif room in rooms['roomsFull'].keys():
            roomObj = rooms['roomsFull'][room]
        return roomObj
    return None

def checkForEmptyness(x):
    #print('In Emptiness check')
    if x in roomNames:
        if x in rooms['roomsOpen']['roomsIdle'].keys():
            #print(rooms['roomsOpen']['roomsIdle'][x])
            if len(rooms['roomsOpen']['roomsIdle'][x]['colorsLeft']) == 4:
                rooms['roomsOpen']['roomsIdle'].pop(x)
                roomNames.remove(x)
                dynamicRooms.remove(x)
        elif x in rooms['roomsOpen']['roomsOngoing'].keys():
            if len(rooms['roomsOpen']['roomsOngoing'][x]['colorsLeft']) == 4:
                rooms['roomsOpen']['roomsOngoing'].pop(x)
                roomNames.remove(x)
                dynamicRooms.remove(x)
        elif x in rooms['roomsFull'].keys():
            roomData = rooms['roomsFull'][x]['gameData'].get()
            rooms['roomsOpen']['roomsOngoing' if roomData['started'] else 'roomsIdle'][x] = rooms['roomsFull'][x]
            rooms['roomsFull'].pop(x)
    #print(rooms)
    #print(dynamicRooms)
    #print(roomNames)

if __name__ == "__main__":
    app.run(port=80)
