"use strict"
import Requests from './requests.mjs'
import CookieHelper from './cookies.mjs'
import SpeechSynth from './speechSynth.mjs'
let currentGameData = []
let currentPlayerData = []
let requestOn = true
let translations = {
    crimson: '#f2074a',
    turquoise: '#1bcc96',
    golden: '#bca401', 
    lime: '#f5fa03',  
}
let clockInterval
let time = ''
let turnAlreadyPrepped = false
export default class UIDisplay{
    static starterPack(){
        this.createBoard()
        setTimeout(()=>{
            SpeechSynth.populateVoiceList()
        }, 1000)
        setTimeout(()=>{
            SpeechSynth.populateVoiceList()
        }, 2000)
        setTimeout(()=>{
            SpeechSynth.populateVoiceList()
        }, 3000)
        setTimeout(()=>{
            SpeechSynth.populateVoiceList()
        }, 5000)
        setTimeout(()=>{
            SpeechSynth.populateVoiceList()
        }, 10000)
        UIDisplay.cyclicGameRequest();
    }
    static async createBoard() {
        let table = document.getElementById("table")
        let checkArr = [
            ["turquoise-tile", 44, 56, 57, 58, 59],
            ["crimson-tile", 6, 16, 27, 38, 49],
            ["golden-tile", 114, 71, 82, 93, 104],
            ["lime-tile", 76, 61, 62, 63, 64],
            ["blank-tile", 4, 5, 15, 17, 26, 28, 37, 39, 45, 46, 47, 48, 50, 51, 52, 53, 54, 55,
                65, 66, 67, 68, 69, 70, 72, 73, 74, 75, 81, 83, 92, 94, 103, 105, 115, 116
            ],
            ["tb-border", 56, 57, 58, 59, 61, 62, 63, 64],
            ["rl-border", 16, 27, 38, 49, 71, 82, 93, 104]
        ]
    
        for (let j = 0; j < 11; j++) {
            let row = table.insertRow(j)
            for (let i = 0; i < 11; i++) {
                let cell = row.insertCell(i)
                let tdNumber = j * 11 + i
                cell.setAttribute("id", `field-${tdNumber}`)
                let res = ""
                checkArr.forEach(element => {
                    if (element.includes(tdNumber)) {
                        res += element
                        cell.classList.add("class", element[0])
                    }
                });
            }
        }
        return new Promise(resolve => {
            resolve();
        });
    };
    static async displayPlayerList(response) {
        console.log('inDisplayResponse: ', response)
        let playerList = response.playerData 
        let roomTsarNick = response.roomTsar.nick
        let amIRoomTsar = response.amIroomTsar
        let playersReady = response.playersReady
        let started = response.started
        let whoseTurn = response.whoseTurn
        console.log(playerList)
        console.log(roomTsarNick)
        console.log(amIRoomTsar)
        console.log(playersReady)
        console.log(started)
        console.log(whoseTurn)
        if(JSON.stringify(currentPlayerData)!=JSON.stringify(playerList)){
            currentPlayerData = playerList
            let el = document.getElementById("playerList")
            el.innerHTML='<h1>Players</h1>';
            playerList.forEach(player => {
                let x = document.createElement("div")
                x.setAttribute("class", "list-row")
                x.setAttribute("id", `player-${player.name}`)
                x.style.color = '#acacac'
                el.append(x)
                x.innerHTML = `<div style='margin-top: 0.5rem; width: 2rem; height: 2rem; background-color: ${translations[player.color]}'></div>`
                if(whoseTurn == player.name){
                    x.innerHTML += `<i class="fas fa-angle-right fa-3x"></i>`
                }
                if(encodeURIComponent(roomTsarNick) == player.name){ x.innerHTML+='<i class="fas fa-crown fa-3x"></i>'}
                x.innerHTML += `<p style='width: 30%; margin-left: 2rem' id="player-${player.name}-nick"></p>`
                x.innerHTML+=`
                <div class="Progress_Status" style="margin-left: 2rem">
                    <div id="player-${player.name}-bar" class="innerBar"></div>
                </div>
                <p id="player-${player.name}-ping" style="margin-left: 2rem; width: 25%"> Ping: ${player.ping}ms</p>
                `
                if (encodeURIComponent(CookieHelper.get('pNICK')) == player.name){
                    if (!started){
                        x.innerHTML+=`<button class="btn" style="margin-left: 2rem" id='readySwitch'>Toggle ready</button>`
                    }
                    x.innerHTML+=`<button class="btn" style="margin-left: 2rem" id='leave'>Leave</button>`
                }
                let nickfield = document.getElementById(`player-${player.name}-nick`)
                nickfield.innerText = decodeURIComponent(player.name)
                UIDisplay.displayProgressBar(player.name, player.score, 250)
            })
            playersReady.forEach(player => {
                console.log(player)
                let el = document.getElementById(`player-${encodeURIComponent(player)}`)
                el.style.backgroundColor = 'rgba(141, 255, 124, 0.6)'
                el.style.color = 'black'
            })
            if(amIRoomTsar){
                let el = document.getElementById("playerList")
                el.innerHTML+=`<button class="btn" style="margin-left: 2rem" id='privateSwitch'>Toggle private</button>`
                let insiEl3 = document.getElementById('privateSwitch')
                insiEl3.addEventListener('click', UIDisplay.privatise)
            }
        }
        else{console.log('Nothing changed since the last request')}
        let insiEl2 = document.getElementById('leave')
        if (insiEl2)
            insiEl2.addEventListener('click', UIDisplay.leave)
        if(!started){
            console.log('not started')
            let insiEl = document.getElementById('readySwitch')
            insiEl.addEventListener('click', UIDisplay.validate)
        }
        return new Promise(resolve => {
            resolve();
        });
    };
    static animateThrow(x, y) {
        console.log(x, y)
        let cube = document.getElementById('cube')
        console.log(cube)
        cube.style.webkitTransform = 'rotateX(' + x + 'deg) rotateY(' + y + 'deg)';
        cube.style.transform = 'rotateX(' + x + 'deg) rotateY(' + y + 'deg)';
    };
    static makeActive(playerName) {
        document.getElementsByClassName("hisTurn").forEach(el => {
            el.classList.remove("hisTurn")
        })
        document.getElementById(`player-${player.name}`).classList.add("hisTurn")
    };
    static displayProgressBar(ID, points, maxPoints) {
        let x = document.getElementById(`player-${ID}-bar`)
        x.style.width = (points / maxPoints) * 100 + '%'
        x.innerHTML = points + "&nbsp;&nbsp;&nbsp;points"
    };
    static async cyclicGameRequest(){
        let response = await Requests.request(window.location.pathname+'/gameData', 'POST')
        console.log('response arrived:', response)
        await UIDisplay.renderGameBoard(response.gameData)
        await UIDisplay.displayPlayerList(response)
        while(requestOn){
            await Requests.wait(1000)
            let response = await Requests.request(window.location.pathname+'/gameData', 'POST')
            console.log('response arrived:', response)
            await UIDisplay.renderGameBoard(response.gameData)
            await UIDisplay.displayPlayerList(response)
            if (response.winner){
                if (!document.getElementById('overley'))
                    UIDisplay.overlay(`The winner is: ${response.winner}`)
            }
            else{
                if (response.isMyTurn){
                    if(!clockInterval){UIDisplay.startClock()}
                    UIDisplay.prepTurn(response.hasAlreadyBeenRolled)
                    UIDisplay.updateTime(response.nextTurn)
                }
                else {
                    let elCol = document.getElementsByClassName('pos-token')
                    for (let i = 0; i < elCol.length; i++){
                        elCol[i].classList.remove('pos-token')
                    }
                    elCol = document.getElementsByClassName('pos-dest')
                    for (let i = 0; i < elCol.length; i++){
                        elCol[i].classList.remove('pos-dest')
                    }
                    if(clockInterval){UIDisplay.stopClock()}
                    let el = document.getElementById('rollBtn')
                    el.innerHTML = ''
                    if (turnAlreadyPrepped){turnAlreadyPrepped = false}
                }
            }
            
        }
    };
    static async renderGameBoard(gameData){
        if(JSON.stringify(currentGameData)!=JSON.stringify(gameData)){
            currentGameData = gameData
            for (let i = 0; i < 121; i++){
                let el = document.getElementById(`field-${i}`)
                el.innerHTML = "";
            }
            gameData.forEach(entry => {
                entry.values.forEach(id => {
                    let el = document.getElementById(`field-${id}`)
                    console.log(el, el.children)
                    if(el.children.length == 0){
                        let x = document.createElement("div")
                        x.setAttribute('class', `roundify ${entry.color}-token piece`)
                        el.append(x)
                    }
                })
            })
        }
        else{console.log('Nothing changed since the last request')}
        return new Promise(resolve => {
            resolve();
        });
    };
    static clearInterval(){
        requestOn = false
    };
    static validate(){
        console.log('validating')
        Requests.request('/ready', 'POST')
    };
    static privatise(){
        console.log('prywaciarz')
        Requests.request('/setPrivate', 'POST')
    };
    static updateTime(serverTimestamp){
        time = serverTimestamp
    }
    static overlay(text){
        let el = document.createElement('div')
        console.log(text)
        el.classList.add('overlay')
        el.setAttribute('id', 'overley')
        el.innerHTML += `<p style="display: block; font-size: 7.5vh; margin-top: 42vh; width: 100vw; text-align: center">${text}</p>
                        <br><a href="./list" style="display: block; font-size: 2.5vh; margin-top: 1vh; 
                        width: 100vw; text-align: center">Go back to list</a>`
        document.body.append(el)
    }
    static startClock(){
        clockInterval = setInterval(() => {
            let el = document.getElementById('clockDiv');
            let temp = time - Date.now()
            let minu = Math.floor(temp / 60000);
            let secu = ((temp % 60000) / 1000).toFixed(0);
            el.innerHTML = `<h2>${minu}:${secu}</h2>`
        })
    }
    static stopClock(){
        clearInterval(clockInterval)
        clockInterval = false
        let el = document.getElementById('clockDiv');
        el.innerHTML=''
    }
    static async leave(){
        console.log('leaving')
        let response = await Requests.request(`${window.location.pathname}/leave/${CookieHelper.get('pUUID')}`, 'GET')
        Requests.tryRedirect(response)
    }
    static displayPossibleMoves(moveList){
        console.log(moveList)
        let processed = []
        for (const [key, value] of Object.entries(moveList)) {
            console.log(key, value);
            if (processed.includes(key)){
                let el = document.getElementById(`field-${key}`)
                el.children[0].innerText = parseInt(el.children[0].innerText, 10) + 1
                el.children[0].style.color = 'white'
            }
            else{
                let el = document.getElementById(`field-${key}`)
                let pasVar1 = key
                let pasVar2 = value
                console.log('IMPORTANT VARS:', pasVar1, pasVar2)
                el.children[0].classList.add('pos-token')
                el.children[0].addEventListener('mouseenter', function(){
                    console.log(pasVar2)
                    UIDisplay.highlight(pasVar2)
                })
                el.children[0].addEventListener('mouseleave', function(){
                    console.log(pasVar2)
                    UIDisplay.lowlight(pasVar2)
                })
                el.children[0].addEventListener('click', function(){
                    console.log(pasVar1)
                    let elCol = document.getElementsByClassName('pos-token')
                    for (let i = 0; i < elCol.length; i++){
                        elCol[i].classList.remove('pos-token')
                    }
                    elCol = document.getElementsByClassName('pos-dest')
                    for (let i = 0; i < elCol.length; i++){
                        elCol[i].classList.remove('pos-dest')
                    }
                    Requests.request('/makeMove', 'POST', {'chosenTile': pasVar1})
                })
                processed.push(pasVar1)
            }
        }
    }
    static lowlight(id){
        console.log('In lowlight')
        console.log(id)
        let el = document.getElementById(`field-${id}`)
        console.log(el)
        el.classList.remove('pos-dest')
    }
    static highlight(id){
        console.log('In highlight')
        console.log(id)
        let el = document.getElementById(`field-${id}`)
        el.classList.add('pos-dest')
    }
    static async roll(){
        let el = document.getElementById('rollBtn')
        el.innerHTML = ""
        let response = await Requests.request('/rollDice', 'POST')
        turnAlreadyPrepped = false
        let data = response.moveData
        console.log("=================")
        console.log("IMPORTANT!!!!!")
        console.log(response)
        UIDisplay.doThingWithRoll(data)
    }
    static doThingWithRoll(data){
        console.log("in do things:", data)
        let x = data.diceData.x*90 + Math.floor(Math.random()*7)*360
        let y = data.diceData.y*90 + Math.floor(Math.random()*7)*360
        UIDisplay.animateThrow(x, y)
        SpeechSynth.speak(data.diceData.number)
        UIDisplay.displayPossibleMoves(data.movesData)
    }
    static prepTurn(hasAlreadyBeenRolled){
        if(turnAlreadyPrepped || hasAlreadyBeenRolled){}
        else{
            try{ 
                let el = document.getElementById('rollBtn')
                let x = document.createElement('button')
                x.setAttribute('class', 'rollBtn button')
                x.innerText = 'Roll!'
                x.addEventListener('click', UIDisplay.roll)
                turnAlreadyPrepped = true
                el.append(x)
            } catch(er) {
                console.log(er)
            }
        }
    }
};
