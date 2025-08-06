import zmq
import time

c = zmq.Context().socket(zmq.PUSH)
c.connect("tcp://10.1.10.85:5000")
while True:
    c.send_string("hello world")
    time.sleep(1)
