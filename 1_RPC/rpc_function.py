import paho.mqtt.client as paho
import time
import serial
import matplotlib.pyplot as plt
import numpy as np
mqttc = paho.Client()

# time parameter
t = np.arange(0,10,0.1) # time vector; create Fs samples between 0 and 10 sec.
y1k = np.arange(0,10,0.1)
y2k = np.arange(0,10,0.1)
# Num time parameter
tn = np.arange(0,10,1) # time vector; create Fs samples between 0 and 10 sec.
ynk = np.arange(0,10,1)

# Settings for connection
host = "localhost"
topic= "velocity"
port = 1883

# Callbacks
def on_connect(self, mosq, obj, rc):
    print("Connected rc: " + str(rc))

def on_message(mosq, obj, msg):
    print("[Received] Topic: " + msg.topic + ", Message: " + str(msg.payload) + "\n");

def on_subscribe(mosq, obj, mid, granted_qos):
    print("Subscribed OK")

def on_unsubscribe(mosq, obj, mid, granted_qos):
    print("Unsubscribed OK")

# Set callbacks
mqttc.on_message = on_message
mqttc.on_connect = on_connect
mqttc.on_subscribe = on_subscribe
mqttc.on_unsubscribe = on_unsubscribe

# Connect and subscribe
print("Connecting to " + host + "/" + topic)
mqttc.connect(host, port=1883, keepalive=60)
mqttc.subscribe(topic, 0)

# XBee setting
serdev = '/dev/ttyUSB0'
s = serial.Serial(serdev, 9600)

s.write("+++".encode())
char = s.read(2)
print("Enter AT mode.")
print(char.decode())

s.write("ATMY 0x140\r\n".encode())
char = s.read(3)
print("Set MY 0x140.")
print(char.decode())

s.write("ATDL 0x240\r\n".encode())
char = s.read(3)
print("Set DL 0x240.")
print(char.decode())

s.write("ATID 0x1\r\n".encode())
char = s.read(3)
print("Set PAN ID 0x1.")
print(char.decode())

s.write("ATWR\r\n".encode())
char = s.read(3)
print("Write config.")
print(char.decode())

s.write("ATMY\r\n".encode())
char = s.read(4)
print("MY :")
print(char.decode())

s.write("ATDL\r\n".encode())
char = s.read(4)
print("DL : ")
print(char.decode())

s.write("ATCN\r\n".encode())
char = s.read(3)
print("Exit AT mode.")
print(char.decode())

print("start sending RPC")

for xn in range(0,int(10)):
    
    # send RPC to remote
    s.write(bytes("\r", 'UTF-8'))
    line=s.readline() # Read an echo string from K66F terminated with '\n' (pc.putc())
    print(line)
    line=s.readline() # Read an echo string from K66F terminated with '\n' (RPC reply)
    print(line)
    time.sleep(1)

    s.write(bytes("/getVec/run\r", 'UTF-8'))
    line=s.readline() # Read an echo string from K66F terminated with '\n' (pc.putc())
    print(line)
    line=s.readline() # Read an echo string from K66F terminated with '\n' (RPC reply)
    print(line)
    time.sleep(1)
    # Record vec from PC
    for x in range(0,int(100)):
        line=s.readline() # Read an echo string from K66F terminated with '\n'
        y1=line.decode().strip().split(" ")[0]
        y1k[x] = float(y1)
        y2=line.decode().strip().split(" ")[1]
        y2k[x] = float(y2)

    # update vel and tilt results to mqtt
    mesg = {y1k, y2k}
    mqttc.publish(topic, mesg)
    print(mesg)