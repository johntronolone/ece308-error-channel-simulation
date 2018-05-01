import logging
import socket

import channelsimulator
import utils
import tcp_segment

def get_frames(data_bytes,d_size):
        n_frames = len(data_bytes) // d_size
        extra = len(data_bytes) % d_size
        pad = 512-extra
        out = []
        for n in range(1,n_frames+1):
            bf = data_bytes[(n-1)*d_size:n*d_size]
            out.append(bf)
            #out.append(interleave(bf[0:128])+interleave(bf[128:256])+interleave(bf[256:384])+interleave(bf[384:512]))
        if extra > 0:
            last = data_bytes[n_frames*d_size:] + bytearray([0]*pad) # zero padding
            out.append(last)
            #out.append(interleave(last[0:128])+interleave(last[128:256])+interleave(last[256:384]) +interleave(last[384:512]))
        return out
        
def interleave(data_bytes): # BRO interleaver 
        data = list(data_bytes)
        out = [0]*128
        for i in range(0,128):
            o = int("0b"+"{:07b}".format(i)[::-1],2)
            out[o] = data[i]
        return bytearray(out)
    
def deinterleave(data_bytes): # BRO deinterleaver 
        data = list(data_bytes)
        out = [0]*128
        for i in range(1,128):
            o = int("0b"+"{:07b}".format(i)[::-1],2)
            out[i-1] = data[o-1]
        return bytearray(out)

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

class TCPSender(Sender):
    
    MSS = 1024
    seq = 0
    
    def __init__(self):
        super(TCPSender, self).__init__()
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
            
    def send(self,data):
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        data_frames = get_frames(data)
        segment = tcp_segment.Segment()
        isn = 0
        seq = isn
        ackn = 0
        rcv_win = 0
        head_len = 16
        d_size = 512
        lsn = 100 # this many +1 different possible sequence #s
        packets = []
        for f in data_frames:
            np = tcp_segment.make_pkt(segment,seq,ackn,rcv_win,f)
            packets.append(np)
            seq += head_len + d_size
            if f > isn + (head_len + d_size)*lsn:
                seq = isn
        while True:
            try:
        #while self.state == 0:
                for p in packets:
                    self.simulator.put_to_socket(p) # send data
                self.state = 1
        #while self.state == 1:
                ack = self.simulator.get_from_socket()  # receive ACK
                #a_check = ack(128:144)
                a_check = tcp_segment.checksum(ack)
                if (a_check == [0,0] and ack[0:4] == seq):
                    break
            except socket.timeout:
                pass
        return packets
if __name__ == "__main__":
    # test out BogoSender
    #sndr = BogoSender()
    #sndr.send(BogoSender.TEST_DATA)
    tcp_sndr = TCPSender()
    h = channelsimulator.random_bytes(512)
    #hint = interleave(h)
    #dhint = deinterleave(hint)
    TCPSender.send(tcp_sndr,h)