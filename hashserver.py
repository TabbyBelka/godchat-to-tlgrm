from urllib import request, parse, error
import json, time, re
import configparser, os
from threading import Timer

config=configparser.ConfigParser(allow_no_value=True)
config.read(os.getenv('FRONTEND_CONFIG'))
config.read(os.getenv('BACKEND_CONFIG'))
config.read(os.getenv('DUNGEON_CONFIG'))

dungRegex = re.compile("(^|\D):(\d{2})(\D|$)")
url = "https://api.telegram.org/bot" + config['bot']['token'] + "/sendMessage"
chatID=config['chat']['commonID']
dungChatID=config['chat']['dungID']
cancelCommand=config['command']['cancel'].lower()
reminderMinDelaySeconds=int(config['reminder']['mindelayseconds'])
reminderSeconds=int(config['reminder']['secondsbefore'])
lasttime = 0
messages = set()

def sendMessage(chatid, textmessage):
    data = parse.urlencode({'text':textmessage, 'chat_id': chatid, 'disable_web_page_preview':'true'}).encode()
    while True:
        req =  request.Request(url, data=data) # this will make the method "POST"
        try:
            resp = request.urlopen(req)
        except error.HTTPError as httperror:
            if httperror.status == 429:
                print("too many requests")
                time.sleep(60)
            elif httperror.status != 200:
                print("common httperror")
                time.sleep(1)
            continue
        except error.URLError:
            print("network error")
            time.sleep(5)
            continue
        time.sleep(0.2)
        break

activeTimers={}

def findNextTimeWithMinutes(curTime, minutes):
    timeMinutes=curTime//60%60
    intMinutes=int(minutes)
    if timeMinutes > intMinutes:
        return (curTime//60//60+1)*60*60 + intMinutes*60
    else:
        return curTime//60//60*60*60 + intMinutes*60

def sendReminder(timer, originmessage):
    sendMessage(dungChatID, "Reminder: "+originmessage[2])
    activeTimers.pop(timer, None)

def handleDungTimer(timer, message, textmessage):
    messageTime=message[0]
    sendMessage(dungChatID, textmessage)
    if cancelCommand in message[2].lower():
        cancellingTimer=activeTimers.get(timer)
        if cancellingTimer is not None:
            print('[info]timer :'+timer+' cancelled')
            cancellingTimer.cancel()
            activeTimers.pop(timer, None)
        return
    jumpTime=findNextTimeWithMinutes(message[0], timer)
    curTime = time.time()+3*60*60
    if jumpTime - messageTime > reminderMinDelaySeconds and jumpTime > curTime:
        print('[info]reminder is set ' + str(jumpTime-curTime-reminderSeconds))
        reminderTimer=Timer(jumpTime-curTime-reminderSeconds, sendReminder, [timer, message])
        prevTimer=activeTimers.get(timer)
        if prevTimer is not None:
            print('[warn]unexpected timer')
            prevTimer.cancel()
        activeTimers[timer]=reminderTimer
        reminderTimer.start()

while True:
    with open(config['paths']['message_pipe'], "r", encoding="utf-8") as f:
        while True:
            try:
                numb = int(f.readline())
            except ValueError:
                break;
            message = tuple(json.loads(f.read(numb)))
            if message[0]>lasttime or message[0]==lasttime and message[1:] not in messages:
                if message[0]>lasttime:
                    messages=set()
                    lasttime = message[0]
                messages.add(message[1:])
                textmessage = time.strftime("[%d.%m %H:%M] ", time.gmtime(message[0]))+message[1]+': '+message[2]
                sendMessage(chatID, textmessage)

                timerMatch=dungRegex.search(message[2])
                if timerMatch:
                    timer=timerMatch.groups()[1]
                    handleDungTimer(timer, message, textmessage)
