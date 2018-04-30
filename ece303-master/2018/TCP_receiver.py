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
        expectedSeqNum = 11090

        timeout = 10
        timeout_start = time.time()
        
        # this will loop until timeout is reached
        while time.time() < timeout_start + timeout: 
            
            while True: # break this loop when packet has been successfully received, else keep attempting to receive packet from channel
                # create mock segment... TODO: actually receive segment from channel
                seg = tcp_segment.Segment()
                seqn = expectedSeqNum
                ackn = 0            
                rcv_win = 0
                #data_bytes = 0
                data_bytes = channelsimulator.random_bytes(104)
                rcv_pkt = seg.make_pkt(seqn, ackn, rcv_win, data_bytes)
                rcvChecksum = rcv_pkt[160:191]

                print 'hello'
#                print list(rcv_pkt[0:4])
                print list(tcp_segment.checksum(rcv_pkt))
                
                # TODO: sum each byte of rcv_pkt, (with each summand a 16-bit integer made from the data)
                        
                print list(rcv_pkt[20:22])

#                print int('{:032b}'.format(rcv_pkt[0:4]))
    #                print(bytearray([113,123,155]))
                
                #rcvSeqNum = '{:032b}'.format(rcv_pkt[0:4])
                rcvSeqNum = 0;
                rcvAckNum = rcv_pkt[32:63]
    
                #print rcvSeqNum                

                
                #computedChecksum = tcp_segment.checksum(rcv_pkt)
                    
                computedChecksum = 0

                # TODO: log that packet received
            
                # implement rdt2.2 receiver

                isCorrupt = True
                hasCorrectSeqNum = False

                # check if sequence number of received packet matches expected
                if rcvSeqNum == expectedSeqNum:
                    hasCorrectSeqNum = True
                else:
                    hasCorrectSeqNum = False

                # check if checksum of received packet is correct
                if rcvChecksum == computedChecksum:
                    isCorrupt = False
                else:
                    isCorrupt = True      

                # act on the above conditions
            
                # if valid
                #if (hasCorrectSeqNum and not isCorrupt):
                    # do stuff
                    # send ack with expectedSeqNo+1
                    # do i need to call tcp_segment.Segment() each time i make a packet??????????
                    #ack_pkt = seg.make_pkt(rcvAckNum, expectedSeqNum+1, rcv_win, data_bytes)
                    #self.simulator.put_to_socket(ack_pkt)
                    #self.logger.info("Got data from socket: {}".format(data.decode('ascii')))
                    # TODO: log ack for successfully received packet
                #    break
                #else: # not valid packet
                    # send ack with expectedSeqNo
                    #ack_pkt = seg.make_pkt(rcvAckNum, expectedSeqNum, rcv_win, data_bytes)
                    
                    #self.simulator.put_to_socket(ack_pkt)
                    #self.logger.info("Got data from socket: {}".format(data.decode('ascii')))
                    # TODO: log ack for retransmission request
                    # loop again
               
                # this loop will keep sending acks until packet is successfully received

 
            # when this point in the loop is reached, a packet has been successfully received
            # increase expectedSeqNo and add 10 seconds to timeout
                #print 'this should print...'
                expectedSeqNum += 1
                print(expectedSeqNum)
                timeout += 10

        # END TIME.TIME() loop


if __name__ == "__main__":
    rcvr = TCP_Receiver()
    rcvr.receive()
