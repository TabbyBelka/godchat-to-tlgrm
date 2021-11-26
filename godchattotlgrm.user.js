// ==UserScript==
// @name         Chat to Telegram
// @namespace    https://godville.net/
// @version      0.3
// @description  Send chat messages to the telegram channel
// @author       Belka
// @match        https://godville.net/superhero
// @grant        GM_xmlhttpRequest
// @run-at       document-idle
// @connect      46.229.213.219
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

      console.log(body)
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
  var sendToBot = function(time, user, message) {
    var d = new Date();
    var curHour = d.getHours();
    var curMinute = d.getMinutes();
    var parsedMesTime = mesTimespampRegex.exec(time);
    if (parsedMesTime === null) {
      return true;
    }
    var mesDate;
    if (parsedMesTime[1] == undefined) {
      var extday = 0;
      if (curHour < +parsedMesTime[4] || (curHour == +parsedMesTime[4] && curMinute < +parsedMesTime[5])) {
        extday = -1;
      }
      mesDate = new Date(d.getFullYear(), d.getMonth(), d.getDate()+extday, +parsedMesTime[4], +parsedMesTime[5]);
    }
    else {
      mesDate = new Date(2000 + +parsedMesTime[3], +parsedMesTime[2], +parsedMesTime[1], +parsedMesTime[4], +parsedMesTime[5]);
    }

    MessageQueue.push([mesDate.getTime()/1000-mesDate.getTimezoneOffset()*60, user, message]);
  };
  setTimeout(function() {
    var target = $('.chat_ph');

    var observer = new MutationObserver(function(mutations) {
      mutations.forEach(function(mutation) {
        if (typeof mutation.addedNodes == "object") {
          var next = $(mutation.addedNodes).find('.gc_fr_el').each( function() {
            var next = $(this);
            if(next && next.attr("title") && next.attr("title").match(/[0-2]?[0-9]:[0-6][0-9] /)) {
              var j = next.prev();
              var message = next.parent().parent().clone().children().remove("*:not(a)").end().text();
              var user = j.text();
              var time = next.attr("title");
              sendToBot(time, user, message);
            }
          });
        }
      });
    });

    var config = { childList: true, subtree: true }

    observer.observe(target.get(0), config);
  },1000);
})();

