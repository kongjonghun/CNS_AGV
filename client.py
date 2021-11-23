import asyncio
from os import name
import socketio
from flask_socketio import send, emit
import threading
import json

REPORT_JSON = {
    'DATA_TYPE':'report',
    'AGV_NO':'AGV00001',
    'LOCATION':'00010002',
    'STATE':'1',
    'MODE':'1',
    'DIRECTION':'0',
    'MAX_VELOCITY':'2.5',
    'TILT_MAX_ANGLE':'20',
    'BELT_MAX_SPEED':'1.5',
    'COMMAND_WAIT_TIME':'10',
    'MIN_VOLTAGE':'15.6',
    'BATTERY_LVL':'30',
    'AGV_FIRMWARE_VERSION':'1.01'
}

ALARM_JSON = {
    'DATA_TYPE':'alarm',
    'AGV_NO':'AGV0001',
    'ALARMS':[
        {
            'ALARM_CD':'11',
            'ALARM_STATUS':'1',
            'OCCUR_DT':'20210817 13:44:22',
        },
        {
            'ALARM_CD':'12',
            'ALARM_STATUS':'0',
            'OCCUR_DT':'20210817 13:44:22',
            'END_DT':'20210817 13:46:55',
        }
    ]
}

sio = socketio.AsyncClient()

@sio.event
async def connect():
    # 알람 전송 백그라운드 실행
    await sio.start_background_task(send_alarm)

@sio.event()
async def disconnect():
    print('disconnected from server')

async def send_alarm():
    while True:
        await sio.sleep(1)
        await sio.emit('alarm_report',json.dumps(ALARM_JSON))

# AGV 상태요청 받기
@sio.on('state_request')
async def state(data):
    await sio.sleep(0.01)
    data = json.loads(data)

    # 상태요청 받으면 상태 전송
    if data['DATA_TYPE'] == 'reportRqst':
        await sio.emit('state_report',json.dumps(REPORT_JSON))

@sio.on('move_request')
async def move_agv(data):
    print(json.dumps(data))

async def main():
    await sio.connect('http://13.124.72.207:5000',headers={'AGV_NO':'AGV00001'})
    #await sio.connect('http://127.0.0.1:5000',headers={'AGV_NO':'AGV00001'})
    await sio.wait() 

if __name__ == '__main__':
    asyncio.run(main()) 