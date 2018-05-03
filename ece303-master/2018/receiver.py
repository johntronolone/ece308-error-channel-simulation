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
    #ACK_DATA = bytes(420)

    def __init__(self):
        super(TCP_Receiver, self).__init__()

    def receive_single(self):

        isn = 0
        lsn = 100
        
        # TODO: add session to log
        #self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        
        # initialize sequence number
        expectedSeqNum = 0
        
        data_bytes = bytearray(512) 
        rcv_win = 255

        timeout = 15
        timeout_start = time.time()
        
        # this will loop until timeout is reached
        #while time.time() < timeout_start + timeout: 
        
        #idx = 1
        segment = tcp_segment.Segment()
        ack_pkt = segment.make_pkt(0, 0, 0, data_bytes)
        numUnAckPkts = 0;
        while True: # break this loop when packet has been successfully received, else keep attempting to receive packet from channel
                    
            data = self.simulator.get_from_socket() 
            #self.logger.info(               #print 'received data from socket: {}'.format(data.decode('ascii'))
             #)
              
            #subdata = data[16:]

            #self.logger.info("Got data from socket: {}".format(subdata.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
            workable_data = list(data)

            #print workable_data                
                
            rcvSeqNum = int("{:08b}".format(workable_data[0]) + "{:08b}".format(workable_data[1]) + "{:08b}".format(workable_data[2]) + "{:08b}".format(workable_data[3]), 2) 
            #print 'LOOK HERE:'
            #print rcvSeqNum
            #rcvAckNum = int("{:08b}".format(workable_data[4]) + "{:08b}".format(workable_data[5]) + "{:08b}".format(workable_data[6]) + "{:08b}".format(workable_data[7]), 2) 
            
            rcvAckNum = 4294967295
            computedChecksum = tcp_segment.checksum(data)
                 
            isCorrupt = True
            hasCorrectSeqNum = False


                # check if sequence number of received packet matches expected
            if rcvSeqNum == expectedSeqNum:
                hasCorrectSeqNum = True
            else:
                hasCorrectSeqNum = False

                # check if checksum of received packet is correct
            if computedChecksum == [0, 0]:
                isCorrupt = False
            else:
                isCorrupt = True      

            if hasCorrectSeqNum is True and isCorrupt is False:
                numUnAckPkts +=1
            else:
                numUnAckPkts = 0
                
            if hasCorrectSeqNum and not isCorrupt:
                #segment = tcp_segment.Segment()
                    # create ACK packet whose sequence number is the ACK number of the received packets, ACK number is sequence number + 1 of received packet (asking for the next packet) 
                ack_pkt = segment.make_pkt(rcvAckNum, rcvSeqNum, rcv_win, data_bytes)
                self.simulator.u_send(ack_pkt)
                #self.simulator.put_to_socket(ack_pkt)
                print 'receiver: ack sent for sequence number:'
                print expectedSeqNum                

                expectedSeqNum = rcvSeqNum + 16 + 512
                
                if expectedSeqNum > isn + (16 + 512)*lsn:
                    expectedSeqNum = isn
                 

#if expectedSeqNum == 
                #    expectSeqNum = 0 
            else:
                #segment = tcp_segment.Segment()
                #nak_pkt = segment.make_pkt(rcvAckNum, expectedSeqNum, rcv_win, data_bytes)
                #self.simulator.u_send(nak_pkt)
                self.simulator.u_send(ack_pkt)
                #self.simulator.put_to_socket(nak_pkt) 
               
                print 'receiver: nak sent for expected sequence number:'
                print expectedSeqNum - 528
                
            #idx += 1
                 
                #self.simulator.put_to_socket(TCP_Receiver.ACK_DATA)

        #print 'attempting to close port'
        #self.simulator.rcvr_disconnect()
        #timeout += 10

        # END TIME.TIME() loop

    def receive(self):

        isn = 1
        lsn = 100
        
        # TODO: add session to log
        #self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        
        # initialize sequence number
        e_seq = 1 # expected sequence number
        
        data_bytes = bytearray(512) 
        rcv_win = 255
        # this will loop until timeout is reached
        #while time.time() < timeout_start + timeout: 
        
        #idx = 1
        segment = tcp_segment.Segment()
        ack_pkt = segment.make_pkt(0, 0, 0, data_bytes)
        old_ack = ack_pkt
        e_seq = isn
        head_len = 16
        d_size = 512
        numIter = 0
        numUnAckPkts = 0
        to = 4
        start_time = time.time()
        while numIter < 35: # break this loop when packet has been successfully received, else keep attempting to receive packet from channel
            
            numIter +=1

           
            
            data = self.simulator.get_from_socket() 
            workable_data = list(data)
            rcvSeqNum = int("{:08b}".format(workable_data[0]) + "{:08b}".format(workable_data[1]) + "{:08b}".format(workable_data[2]) + "{:08b}".format(workable_data[3]), 2) 
            
            rcvAckNum = 4294967295
            computedChecksum = tcp_segment.checksum(data)
            isCorrupt = True
            hasCorrectSeqNum = False
            #ack_pkt = segment.make_pkt(rcvAckNum, 0, rcv_win, data_bytes) # initial ACK packet
            
            if computedChecksum == [0, 0] and rcvSeqNum == e_seq: # not corrupted and expected sequence #
                isCorrupt = False
                old_ack = ack_pkt
                ack_pkt = segment.make_pkt(rcvAckNum, e_seq, rcv_win, data_bytes) # create but don't send ack
                
                numUnAckPkts +=1

                #self.simulator.u_send(ack_pkt)
                
                print 'packet successfully received with sequence number'
                print e_seq

                e_seq +=  16 + 512
                
                #if e_seq > isn + (16 + 512)*lsn:
                #    e_seq = isn
                #print e_seq
            else:
                isCorrupt = True
                #segment = tcp_segment.Segment()
                #nak_pkt = segment.make_pkt(rcvAckNum, expectedSeqNum, rcv_win, data_bytes)
                #self.simulator.u_send(nak_pkt)
                #self.simulator.u_send(ack_pkt) # discard data, resend last ack #
                self.simulator.put_to_socket(old_ack) # send most recently created ack
               
                print 'receiver: nak sent for expected sequence number:'
                print e_seq
            
            print 'numUnAckPkts:'
            print numUnAckPkts
            print 'time.time():'
            print time.time()
            print 'start_time + to:' 
            print start_time + to
            if numUnAckPkts > 8 or time.time() > to + start_time:
                self.simulator.put_to_socket(ack_pkt)
                print 'receiver: ack sent for sequence number:'
                print e_seq
                numUnAckPkts = 0
                start_time = time.time()
            '''        
            data = self.simulator.get_from_socket() 
            #self.logger.info(               #print 'received data from socket: {}'.format(data.decode('ascii'))
             #)
                
            #subdata = data[16:]

            #self.logger.info("Got data from socket: {}".format(subdata.decode('ascii')))  # note that ASCII will only decode bytes in the range 0-127
            workable_data = list(data)

            #print workable_data                
                
            rcvSeqNum = int("{:08b}".format(workable_data[0]) + "{:08b}".format(workable_data[1]) + "{:08b}".format(workable_data[2]) + "{:08b}".format(workable_data[3]), 2) 
            #print 'LOOK HERE:'
            #print rcvSeqNum
            #rcvAckNum = int("{:08b}".format(workable_data[4]) + "{:08b}".format(workable_data[5]) + "{:08b}".format(workable_data[6]) + "{:08b}".format(workable_data[7]), 2) 
            
            rcvAckNum = 4294967295
            computedChecksum = tcp_segment.checksum(data)
                 
            isCorrupt = True
            hasCorrectSeqNum = False


                # check if sequence number of received packet matches expected
            if rcvSeqNum == expectedSeqNum:
                hasCorrectSeqNum = True
            else:
                hasCorrectSeqNum = False

                # check if checksum of received packet is correct
            if computedChecksum == [0, 0]:
                isCorrupt = False
            else:
                isCorrupt = True      
                
            if hasCorrectSeqNum and not isCorrupt:
                #segment = tcp_segment.Segment()
                    # create ACK packet whose sequence number is the ACK number of the received packets, ACK number is sequence number + 1 of received packet (asking for the next packet) 
                ack_pkt = segment.make_pkt(rcvAckNum, rcvSeqNum, rcv_win, data_bytes)
                self.simulator.u_send(ack_pkt)
                #self.simulator.put_to_socket(ack_pkt)
                print 'ack sent'
                
                expectedSeqNum = rcvSeqNum + 16 + 512
                
                if expectedSeqNum > isn + (16 + 512)*lsn:
                    expectedSeqNum = isn
                 

#if expectedSeqNum == 
                #    expectSeqNum = 0 
            else:
                #segment = tcp_segment.Segment()
                #nak_pkt = segment.make_pkt(rcvAckNum, expectedSeqNum, rcv_win, data_bytes)
                #self.simulator.u_send(nak_pkt)
                self.simulator.u_send(ack_pkt)
                #self.simulator.put_to_socket(nak_pkt) 
               
                print 'receiver: nak sent for expected sequence number:'
                print expectedSeqNum
                
            #idx += 1
                 
                #self.simulator.put_to_socket(TCP_Receiver.ACK_DATA)

        #print 'attempting to close port'
        #self.simulator.rcvr_disconnect()
        #timeout += 10

        # END TIME.TIME() loop
        '''
if __name__ == "__main__":
    rcvr = TCP_Receiver()
    rcvr.receive()
