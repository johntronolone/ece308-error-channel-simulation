import logging

import channelsimulator
import utils

import tcp_segment
#import tcp_segment.Segment

import time


class Receiver(object):
    def __init__(self, inbound_port=50005, outbound_port=50006, timeout=10, debug_level=logging.INFO):
        self.logger = utils.Logger(self.__class__.__name__, debug_level)

        self.inbound_port = inbound_port
        self.outbound_port = outbound_port
        self.simulator = channelsimulator.ChannelSimulator(inbound_port=inbound_port, outbound_port=outbound_port,debug_level=debug_level)
        self.simulator.rcvr_setup(timeout)
        self.simulator.sndr_setup(timeout)

    def receive(self):
        raise NotImplementedError("The base API class has no implementation. Please override and add your own.")


class TCP_Receiver(Receiver):
    #ACK_DATA = bytes(123); #ACK number

    def __init__(self):
        super(TCP_Receiver, self).__init__()

    def receive(self):
        
        # add session to log
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        
        # initialize sequence number
        expectedSeqNum = 0

        timeout = 15
        timeout_start = time.time()
        
        # this will loop until timeout is reached
        while time.time() < timeout_start + timeout: 
            
            while True: # break this loop when packet has been successfully received, else keep attempting to receive packet from channel
                    
                data = self.simulator.get_from_socket() 
                #self.logger.info(
                print 'received data from socket: {}'.format(data.decode('ascii'))
                #)
                
                print data 
                
                # TODO: deinterleave and extract data ...
                    
                # TODO: rcvSeqNum = list(data[0:4])
                # TODO: rcvAckNum = list(data[4:8])
                
                # TODO: rcv_win = all zeros
                # TODO: data_bytes = all zeros

                computedChecksum = tcp_segment.checksum(data)
                
                isCorrupt = True
                hasCorrectSeqNum = False

                # check if sequence number of received packet matches expected
                if rcvSeqNum == expectedSeqNum:
                    hasCorrectSeqNum = True
                else:
                    hasCorrectSeqNum = False

                # check if checksum of received packet is correct
                if computedChecksum == [255, 255]:
                    isCorrupt = False
                else:
                    isCorrupt = True      
                
                if hasCorrectSeqNum and not isCorrupt:
                    segment = tcp_segment.Segment()
                    # create ACK packet whose sequence number is the ACK number of the received packets, ACK number is sequence number + 1 of received packet (asking for the next packet)
                    
                    ack_pkt = segment.make_pkt(rcvAckNum, expectedSeqNum + 1, rcv_win, data_bytes)
                    #self.simulator.put_to_socket(ack_pkt)
                    print 'ack sent'
                    expectedSeqNum += 1
                else:
                    #nak_pkt = segment.make_pkt(
                    #self.simulator.put_to_socket(nak_pkt)                
                    print 'nak sent'
 
                timeout += 10

        # END TIME.TIME() loop


if __name__ == "__main__":
    rcvr = TCP_Receiver()
    rcvr.receive()
