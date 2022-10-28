// ==UserScript==
// @name         Chat to Telegram
// @namespace    https://godville.net/
// @version      0.4
// @description  Send chat messages to the telegram channel
// @author       Belka
// @match        https://godville.net/superhero
// @grant        GM_xmlhttpRequest
// @run-at       document-idle
// @connect      <server url>
// ==/UserScript==

(function() {
  'use strict';
  var ServerIP = <url of mes.py>
  var userToken = <user token from tokens section of frontendconfig>
  var mesTimespampRegex = /^(?:([0-9]{1,2})\.([0-9]{1,2})\.([0-9]{1,2}) )?([0-9]{1,2})\:([0-9]{1,2}) ?$/;
  var MessageQueue = [];
  var sendMessages = function() {
    if(MessageQueue.length != 0) {
      var textmessage = JSON.stringify(MessageQueue);
      MessageQueue = [];
      var body = "token=" + encodeURIComponent(userToken) +
                 "&text=" + encodeURIComponent(textmessage);

      var makeRequest = function() {
        GM_xmlhttpRequest({method: "POST",
          url: ServerIP,
          data : body,
          headers: { 'Content-Type' : 'application/x-www-form-urlencoded'},
          onload: function(res) {
            console.log(res);
            if (res.status == 429) {
              setTimeout(makeRequest, 30000);
            }
            else if(res.status != 200) {
              setTimeout(makeRequest, 500);
            }
            else {
              setTimeout(sendMessages, 200);
            }
          }});
      };
      makeRequest();
    }
    else {
      setTimeout(sendMessages, 2000);
    }
  };
  setTimeout(sendMessages, 3000)
  var lastmid = 0;
  var sendToBot = function(time, user, message, mid) {
    if (mid <= lastmid) return;
    lastmid = mid;
    var d = new Date(time);
    MessageQueue.push([d.getTime()/1000-d.getTimezoneOffset()*60, user, message, mid]);
  };
  var handleAjaxResult = function(res) {
    res.msg.forEach(function(e) {
      sendToBot(e.t, e.u, e.m, e.id);
    });
  };
  setTimeout(function() {
    var originAjax = $.ajax;
    $.ajax = function(a,b) {
      if (a.url.includes('MRsaFLGpTaPol6FFhAtS') ||
          (Object.hasOwn(a.data, 'a') &&
           a.data.a.includes('3GGcSQqPm4DC1ynsBr8l'))) {
        var originSuccess = a.success;
        a.success = function(n) {
          originSuccess(n);
          handleAjaxResult(n);
        };
      }
      originAjax(a,b);
    };
  },1000);
})();

