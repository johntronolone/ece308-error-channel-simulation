import logging
import socket

import channelsimulator
import utils
import tcp_segment

import time

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
            
    def send_single(self,data): # rdt 2.2 sender 
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        d_size = 512
        data_frames = get_frames(data,d_size)
        segment = tcp_segment.Segment()
        isn = 1 # initial sequence #
        ian = 1 # initial acknowledgement #
        seq = isn
        ackn = ian
        rcv_win = 0
        head_len = 16 # header length: 16 bytes
        lsn = 100 # this many +1 different possible sequence #s
        packets = []
        for f in data_frames: # make all packets associate each w/ sequence #
            np = segment.make_pkt(seq,ackn,rcv_win,f)
            packets.append(np)
            seq += head_len + d_size
            ackn += head_len + d_size
            if seq > isn + (head_len + d_size)*lsn: # cycle back to first sequence #
                seq = isn
            if ackn > ian + (head_len + d_size)*lsn:
                ackn = ian
        for p in packets:
            seq = p[0:4]
            self.state = 0
            while self.state == 0:
                try:
                    #self.simulator.u_send(p) 
                    self.simulator.put_to_socket(p) # send data
                    ack = self.simulator.get_from_socket()  # receive ACK
                    #a_check = ack(128:144)
                    a_check = tcp_segment.checksum(ack) # check for corruption
                    #print 'this should appear'
                    #print 'sender: received ack' 
                    #print ack
                    #print 'sender: received ack checksum'
                    #print a_check
                    #print list(ack[4:8])
                    if (a_check == [0,0] and ack[4:8] == seq): # not corrupt and correct seq. #
                        # extract and store data
                        print 'sender: correct ack number and not corrupt'
                        self.state = 1 # send next packet 
                    else:
                        print 'sender: incorrect ack number or corrcupt'
                    #break    
                except socket.timeout:
                    pass
                
    def send(self,data): # Go-Back-N protocol
        self.logger.info("Sending on port: {} and waiting for ACK on port: {}".format(self.outbound_port, self.inbound_port))
        d_size = 512
        data_frames = get_frames(data,d_size)
        segment = tcp_segment.Segment()
        isn = 1 # initial sequence #
        ian = 1 # initial acknowledgement #
        seq = isn
        ackn = ian
        rcv_win = 0
        head_len = 16 # header length: 16 bytes
        #lsn = 100 # this many +1 different possible sequence #s
        last_seq = 0
        packets = []
        for f in data_frames: # make all packets associate each w/ sequence #
            np = segment.make_pkt(seq,ackn,rcv_win,f)
            packets.append(np)
            last_seq = seq
            seq += head_len + d_size
            ackn += head_len + d_size
            #if seq > isn + (head_len + d_size)*lsn: # cycle back to first sequence #
            #    seq = isn
            #if ackn > ian + (head_len + d_size)*lsn:
            #    ackn = ian
        
        pn = 1 # packet number
        b_seq = isn # base sequence number
        w_size = 10 # number of packets in window
        n_seq = b_seq # next sequence #, start at base
        timeout = 0.5
        self.state = 0
        while self.state == 0:
            w_end = (b_seq + w_size*(head_len + d_size))
            #max_seq = (ian + (head_len + d_size)*lsn)
            #overflow = w_end - max_seq
            #rem_space = max_seq - n_seq
            pn = 1 
            while n_seq < w_end and pn <=len(packets): # or (overflow > 0 and rem_space + overflow > 0): # send all segments in window
                #np = (n_seq - b_seq)/(head_len + d_size) # number of segments to send
                #if pn <= len(packets):
                #self.simulator.u_send(packets[pn-1])                
                self.simulator.put_to_socket(packets[pn-1])
                print 'sender: sent packet of index (pn):' 
                print pn
                print 'sender: with seq number'
                print n_seq
                #self.simulator.put_to_socket(packets[pn-1]) #[pn-1]
                if b_seq == n_seq:
                    timeout_start = time.time()
                n_seq += (head_len + d_size) 
                #if rem_space <= 0: # wrap around next sequence #
                #    n_seq = isn
                pn += 1
                #rem_space = max_seq - n_seq
                #print 'sent equence number:'
                #print n_seq
                #print w_end
            ack = self.simulator.get_from_socket()
            #r_seq = ack[4:8] # acknowledgment number
            r_seq = int("{:08b}".format(ack[4]) + "{:08b}".format(ack[5]) + "{:08b}".format(ack[6]) + "{:08b}".format(ack[7]), 2)
            print 'ack received with seq number:'
            print r_seq 
            r_check = tcp_segment.checksum(ack)
            boo = True
            if r_check == [0,0]:  # not corrupted
                if r_seq == [0]*4: # check for initial case
                    break
                else:
                    pn = (r_seq - 1)/528 - 1

                    b_seq = r_seq + (head_len + d_size) - 528 # increase base of window
                    w_end = (b_seq + w_size*(head_len + d_size))
                    #if w_end > max_seq:
                    #    w_end = isn + w_end - max_seq
                #if b_seq > max_seq: # wrap around base sequence #
                    #b_seq = isn
                    #w_end = (b_seq + w_size*(head_len + d_size))
                if b_seq == n_seq:
                    #timeout_start = time.time() # pause timer
                    boo = False # pause timer
                    #break # stop timer
                else:
                    timeout_start = time.time() # restart timer

            print ''
            print 'pn:'
            print pn
            print 'len(packets)'
            print len(packets)
            print 'b_seq:'
            print b_seq
            print 'last_seq'
            print last_seq
            print 'r_seq'
            print r_seq
            print ''
            if pn == len(packets) and r_seq == last_seq: # reached last segment #b_seq == last_seq and 
                print 'this should print?'
                self.state = 1
            if time.time() > timeout_start+timeout or boo is True: # timeout or timer paused
                self.logger.info("Timeout on seqence number: {}. Resending...".format(b_seq))
                np = (n_seq - b_seq)/(head_len + d_size) 
                pn -= np
                n_seq = b_seq # reset next sequence + to base of window
                #timeout_start = time.time()
            if r_seq == last_seq:
                self.state = 1
        '''
        for p in packets:
            seq = p[0:4]
            self.state = 0
            while self.state == 0:
                try:
                    self.simulator.u_send(p) 
                    #self.simulator.put_to_socket(p) # send data
                    ack = self.simulator.get_from_socket()  # receive ACK
                    #a_check = ack(128:144)
                    a_check = tcp_segment.checksum(ack) # check for corruption
                    #print 'this should appear'
                    #print 'sender: received ack' 
                    #print ack
                    #print 'sender: received ack checksum'
                    #print a_check
                    #print list(ack[4:8])
                    if (a_check == [0,0] and ack[4:8] == seq): # not corrupt and correct seq. #
                        # extract and store data
                        print 'sender: correct ack number and not corrupt'
                        self.state = 1 # send next packet 
                    else:
                        print 'sender: incorrect ack number or corrcupt'
                    #break    
                except socket.timeout:
                    pass
        '''
        '''
        # GO-BACK-N implementation 
        b_seq = 0 # base sequence number
        w_size = 10 # number of packets in window
        n_seq = b_seq # next sequence #, start at base
        timeout = 0.2
        while n_seq < b_seq + w_size*(head_len + d_size):
            self.simulator.put_to_socket(packets[n_seq])
            if b_seq == n_seq:
                timeout_start = time.time()
            b_seq += (head_len + d_size)
        ack = self.simulator.get_from_socket()
        r_seq = ack[0:4]
        r_check = tcp_segment.checksum(ack)
        if r_check == [0,0]:
            b_seq = 
            
        if time.time() == timeout_start+timeout:
            self.logger.info("Timeout on seqence number: {}. Resending...".format(b_seq))
            timeout_start = time.time()
            r_packets = packets[]
        '''
if __name__ == "__main__":
    # test out BogoSender
    #sndr = BogoSender()
    #sndr.send(BogoSender.TEST_DATA)
    tcp_sndr = TCPSender()
    data_size = 20000 # number of bytes in data
    h = channelsimulator.random_bytes(data_size)
    #hint = interleave(h)
    #dhint = deinterleave(hint)
    start_time = time.time()
    TCPSender.send(tcp_sndr,h)
    elapsed_time = time.time() - start_time
    print "Elapsed Time: {} seconds".format(elapsed_time)
    thruput = "Throughput: {} Kbps".format(data_size/elapsed_time)
    print thruput
