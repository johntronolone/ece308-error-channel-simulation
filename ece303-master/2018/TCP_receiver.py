import logging

import channelsimulator
import utils

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
        ################
        # python code
        
        # add session to log
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        

        # initialize sequence number

        expectedSeqNo = 0

        while True:
            
            # receive data
            data = self.simulator.get_from_socket()
            
             
            
            # rcvChecksum is checksum received in packe
            rcvChecksum = data[160:191]

            # computedChecksum is checksum computed from packet
            computedChecksum = rcvChecksum
            # insert computedChecksum function from stephen's sender
            
            # rcvSeqNo is sequence number of received TCP segment
            rcvSeqNo = data[0:31]
            
            
            corrupt = True
            correctSeqNo = False
            
            # check sequence number
            if (rcvSeqNo == expectedSeqNo)
                correctSeqNo = True
            else
                correctSeqNo = False

            
            if (rcvChecksum == computedChecksum)
                corrupt = False
            else
                corrupt = True             

            # check checksum
            if (correctSeqNo && !corrupt)
                # extract and deliver data
                # send ACK for seqNo + 1 (next expected packet)
                ack_pkt = bytearray([0, expectedSeqNo+1,]) ... ntf
                self.simulator.put_to_socket(ack_pkt)
                # increase expected sequence number
            else
                # send NAK which is actually ACK for current seqNo
                ack_pkt = bytearray([expectedSeqNo]) ... ntf
                self.simulator.put_to_socket(ack_pkt)

            
            # log received data
            self.logger.info("Got data from socket: {}".format(data.decode('ascii')))

            
            ################
            # rdt code
            # implement state machine
        
            # send ACK
            self.simulator.put_to_socket(TCP_Receiver.ACK_DATA)


if __name__ == "__main__":
    rcvr = TCP_Receiver()
    rcvr.receive()
