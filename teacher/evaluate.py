# -*- coding: utf-8 -*-
from openpyxl import Workbook
from openpyxl import load_workbook
import hashlib
import json
from websocket import create_connection
import time
import os
import fnmatch

AUDIO_FORMAT = "wav"
SAMPLE_RATE = "16000"


def runEval(reftext, audioPath, kernel):

    if(kernel == 'pred.exam'):
        coretype = "en.pred.exam"
        refText = reftext
    elif(kernel == 'sent.recscore'):
        coretype = "en.sent.recscore"
        refText = reftext
    elif(kernel == 'sent.score'):
        coretype = "en.sent.score"
        refText = reftext

    allfile = []
    allfile.append(audioPath)

    for filename in allfile:
        print('current audio:' + filename)
        rstJson = start(filename, refText, coretype)
        print('eval result:' + rstJson)

    return rstJson


def getTimestamp():
    return int(round(time.time()*1000))


def getSig(appkey, timestamp, secretkey):
    sigStr = appkey+str(timestamp)+secretkey
    return hashlib.sha1(sigStr.encode('utf-8')).hexdigest()


def start(audioPath, refText, coreType):
    serverurl = "ws://cloud.chivox.com/ws?e=0&t=0&version=2"
    ws = create_connection(serverurl)
    appkey = "appKey"
    secretkey = "seacretKey"
    timestamp = getTimestamp()
    sig = getSig(appkey, timestamp, secretkey)
    validate_msg = {
        "app": {
            "sig": sig,
            "applicationId": appkey,
            "timestamp": str(timestamp),
            "userId": "chivox_evalsys",
            "alg": "sha1"}}
    validate_msg_json = json.dumps(validate_msg)
    ws.send(validate_msg_json)

    print(refText)
    request_param = {
        "request": {
            "attachAudioUrl": 1,
            "refText": refText,
            "rank": 100,
            "precision": 1,
            "coreType": coreType, },
        "audio": {
            "sampleBytes": 2,
            "channel": 1,
            "sampleRate": SAMPLE_RATE,
            "audioType": AUDIO_FORMAT}
    }

    request_json = json.dumps(request_param)
    print('request_param: ' + request_json)
    ws.send(request_json)
    f = open(audioPath, 'rb')
    data = ""
    count = os.path.getsize(audioPath)
    while count > 0:
        if count < 1024:
            data = f.read(count)
            count = count - count
            ws.send_binary(data)
        else:
            data = f.read(1024)
            count = count - 1024
            ws.send_binary(data)
    ws.send_binary("")
    f.close()
    result = ws.recv()
    ws.close()
    return json.dumps(json.loads(result), sort_keys=True, indent=2)
