import logging
import socket

import channelsimulator
import utils
import tcp_segment



class Sender(object):

    def __init__(self, inbound_port=50006, outbound_port=50005, timeout=10, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,
                                                           debug_level=debug_level)
        self.simulator.sndr_setup(timeout)
        self.simulator.rcvr_setup(timeout)
        self.state = 1

    def send(self, data):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class BogoSender(Sender):
    TEST_DATA = bytearray([68, 65, 84, 65])  # some bytes representing ASCII characters: 'D', 'A', 'T', 'A'

    def __init__(self):
        super(BogoSender, self).__init__()

    def send(self, data):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        while True:
            try:
                self.simulator.put_to_socket(data)  # send data
                ack = self.simulator.get_from_socket()  # receive ACK
                self.logger.info("Got ACK from socket: {}".format(
                    ack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                break
            except socket.timeout:
                pass

class TCPSender(BogoSender):
    
    MSS = 1024
    
    def __init__(self):
        super(RdtSender, self).__init__()
        self.state = 0
        self.isn = 0
        
    def setup(self,seq_num):
        self.logger.info("Sending SYN on port: {} and waiting for SYNACK on port: {}".format(self.outbound_port, self.inbound_port))
        syn_head = tcp_segment.Segment(1,0)
        syn_seg = tcp_segment.make_pkt(syn_head,[])
        while True:
            try:
                self.simulator.put_to_socket(syn_seg)  # send data
                synack = self.simulator.get_from_socket()  # receive ACK
                self.logger.info("Got SYNACK from socket: {}".format(
                    synack.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
                break
            except socket.timeout:
                pass
            
    def interchange(data_bytes):
        #bytearray(random.getrandbits(8) for _ in xrange(size))
        out = list()
        for i in range(1,128):
            o = int("0b"+"{:07b}".format(i)[::-1],2)
            out(o) = data_bytes(i)
        return out
            
    def send(self,data):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        while True:
            try:
        #while self.state == 0:
                segment = tcp_segment.Segment(setup=0,teardown=0)
                packet = tcp_segment.make_pkt(segment,data)
                self.simulator.put_to_socket(packet) # send data
                self.state = 1
        #while self.state == 1:
                ack = self.simulator.get_from_socket()  # receive ACK
                #a_check = ack(128:144)
                a_check = tcp_segment.checksum(ack)
                if (a_check == bin(2**16-1)) and (ack(64:95) == seq_num):
                    break
            except socket.timeout:
                pass
            
if __name__ == "__main__":
    # test out BogoSender
    sndr = BogoSender()
    sndr.send(BogoSender.TEST_DATA)