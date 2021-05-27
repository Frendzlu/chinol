export default class CookieHelper {
  static set(name, value, expiry=3600*1000){
    let d = new Date();
    d.setTime(d.getTime() + expiry)
    document.cookie = encodeURIComponent(name) + "=" + encodeURIComponent(value) + ";expires=" + d.toUTCString() + "; SameSite=Lax;path=/";
  }
  static get(name){
    let matches = document.cookie.match(new RegExp(
      "(?:^|; )" + name.replace(/([\.$?*|{}\(\)\[\]\\\/\+^])/g, '\\$1') + "=([^;]*)"
    ));
    return matches ? decodeURIComponent(matches[1]) : undefined;
  };
};
