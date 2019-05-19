import threading

'''
    plus-value
    non commencée
'''

#### DEVELOPPEMENT EN COURS
class Network(threading.Thread):
    def __init__(self,server):
        threading.Thread.__init__(self)
        self.host = server
    def host(self):
        print("en dev")
    def client(self):
        if self.host: return
    def listen(self):
        print("en dev")
    def send(self):
        print("en dev")
    def sendAll(self):
        if not(self.host): return