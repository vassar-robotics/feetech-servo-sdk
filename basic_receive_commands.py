import zmq
s = zmq.Context().socket(zmq.PULL)
s.bind("tcp://0.0.0.0:5000")
while True:
    print(s.recv_string())