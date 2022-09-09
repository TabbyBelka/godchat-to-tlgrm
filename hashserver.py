from urllib import request, parse, error
import json, time, re
import configparser, os

config=configparser.ConfigParser(allow_no_value=True)
config.read(os.getenv('FRONTEND_CONFIG'))
config.read(os.getenv('BACKEND_CONFIG'))

dungRegex = re.compile("(^|\D):\d{2}(\D|$)")
url = "https://api.telegram.org/bot" + config['bot']['token'] + "/sendMessage"
chatID=config['chat']['commonID']
dungChatID=config['chat']['dungID']
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
                if dungRegex.search(message[2]):
                    sendMessage(dungChatID, textmessage)
