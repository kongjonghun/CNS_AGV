import asyncio
from os import name
import socketio
from flask_socketio import send, emit
import threading
import json

test_json = {
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

alarm_json = {
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
    # connect되면 알람 발생
    await send_alarm()

# 알람 전송
async def send_alarm():
    await sio.emit('alarm',json.dumps(alarm_json))

# AGV 상태요청 receive
@sio.on('state')
async def state(data):
    json_data = json.loads(data)

    # 상태보고 전송 Thread 시작
    if json_data['DATA_TYPE'] == 'reportRqst':
        sio.start_background_task(send_state)

# AGV 상태보고 전송
async def send_state():
    while True:
        await sio.emit('state',json.dumps(test_json))
        await sio.sleep(3)

# AGV 이동 명령 receive
@sio.on('move')
async def move_avg(data):
    print(str(data))

# 서버 연결 해제
@sio.event()
async def disconnect():
    print('disconnected from server')

async def main():
    await sio.connect('http://172.31.32.116:5000',headers={'AGV_NO':'AGV00001'})
    await sio.wait() 

if __name__ == '__main__':
    asyncio.run(main()) 