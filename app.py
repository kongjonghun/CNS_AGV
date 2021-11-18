from threading import Lock
from flask import Flask, render_template, session, request, copy_current_request_context
from flask_socketio import SocketIO, emit, join_room, leave_room, close_room, rooms, disconnect
from engineio.payload import Payload
import json

Payload.max_decode_packets = 101
async_mode = None

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app, async_mode=async_mode)
thread = None
thread_lock = Lock()

clients = {}

def background_thread():
    MOVE_JSON = {
        'DATA_TYPE':'moveCommand',
        'AGV_NO':'temp',
        'ACTION':'1',
        'BLOCKS':[
            '00010002',
            '00020003',
        ]
    }

    while True:
        socketio.sleep(3)
        for AGV in clients.keys():
            MOVE_JSON['AGV_NO'] = AGV
            socketio.emit('move',json.dumps(MOVE_JSON), room=clients[AGV])

@socketio.on('connect')
def connect():
    global thread

    clients[request.headers['AGV_NO']] = request.sid

    REPORT_REQUEST = {
        'DATA_TYPE':'reportRqst',
        'AGV_NO':request.headers['AGV_NO'],
    }

    socketio.emit('state',json.dumps(REPORT_REQUEST), room=request.sid)

    with thread_lock:
        if thread is None: 
            thread = socketio.start_background_task(background_thread)

@socketio.on('disconnect')
def disconnect():
    print("disconnected")
    del clients[request.headers['AGV_NO']]

@socketio.on('state')
def state(data):
    print(str(data))

@socketio.on('alarm')
def alarm(data):
    print(str(data))

if __name__=="__main__":
    socketio.run(app)