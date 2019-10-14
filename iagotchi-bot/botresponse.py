from __future__ import print_function, division
import sys, osc, os


class BotResponse(object):
    
    def __init__(self, osc_server_port=5005, osc_client_host='127.0.0.1', osc_client_port=5009):
        self.osc_server_port = osc_server_port
        self.osc_client_host = osc_client_host
        self.osc_client_port = osc_client_port
        self.osc_client = osc.Client(osc_client_host, osc_client_port)
        self.osc_server = osc.Server(host='0.0.0.0', port=osc_server_port, callback=self.osc_server_message)
        self.osc_server.run(non_blocking=True)
        
        self.osc_client.send("/botresponse/ready")
        
        #self.model = torch.load(model_filename, map_location=lambda storage, loc: storage, encoding='utf8')
        #if default_allowed_filename is None:
            #self.allowed = set(self.model.dictionary.idx2word)
        #else:
            #self.allowed = set(open(default_allowed_filename).read().split('\n'))
            #self.allowed.update('.,!:;')
            
        print("Ready For Getting Bot Response")


    def osc_server_message(self, message):
        print("message entrant {}".format(message))
            
        if '/result/botresponse' in message:
            message = message.replace('/result/botresponse', '')
            print('botresponse: {}'.format(message))
        elif '/session/start' in message:
            message = message.replace('/session/start', '')
            print('sesson start at: {}'.format(message))
            
        elif '/session/stop' in message:
            message = message.replace('/session/stop', '')
            print('session stop at: {}'.format(message))
            
        elif '/session/name' in message:
            message = message.replace('/session/name', '')
            print('user name is : {}'.format(message))
        elif message == '/exit':
            self.osc_server.shutdown()
            sys.exit(0)


if __name__ == '__main__':
    BotResponse()
