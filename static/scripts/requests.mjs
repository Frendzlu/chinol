"use strict"
import CookieHelper from './cookies.mjs'
export default class Requests {
  static async sendNick() {
    let nick = document.getElementById("nickname").value
    console.log(window.location.pathname)
    let body = {
      nick: nick,
      calee: window.location.pathname == "" ? '/list' : window.location.pathname
    };
    let response = await Requests.request('/setnick', 'POST', body)
    console.log(response)
    CookieHelper.set('pUUID', response.pUUID)
    CookieHelper.set('pNICK', response.nick)
    Requests.tryRedirect(response)
  };
  static tryRedirect(response){
    if ('redirect' in response){
      console.log('Redirecting: ', response.redirect)
      window.location.href = window.location.origin + response.redirect
    }
  };
  static async request(adress, method, body={}){
    if (['GET', 'HEAD'].includes(method)){
      let response = await fetch(adress, {
        method: method,
        headers: {
        'Content-Type': 'application/json;charset=utf-8'
        },
      });
      console.log(response)
      return await response.json();
    }
    else{
      let response = await fetch(adress, {
        method: method,
        headers: {
        'Content-Type': 'application/json;charset=utf-8'
        },
        body: JSON.stringify(Object.assign({}, body, {time: Date.now()}))
      });
      return new Promise(resolve => {
        resolve(response.json());
      });
    }
  };
  static errorParse(response){
    if ('error' in response){
      let el = document.getElementById('error-div')
      el.innerText = response.error
    }
    else return True;
  };
  static async DOMrequest(adress, method){
    let response = await Requests.request(adress, method)
    console.log(response)
    console.log(response.body)
    Requests.tryRedirect(response)
  };
  static async wait(howMuch){
    return new Promise(resolve => {
      setTimeout(() => {
        resolve();
      }, howMuch);
    });
  };
};
