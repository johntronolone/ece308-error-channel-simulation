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
    ACK_DATA = bytes(123); #ACK number

    print(ACK_DATA);

    def __init__(self):
        super(TCP_Receiver, self).__init__()

    def receive(self):
        ################
        # python code
        
        # add session to log
        self.logger.info("Receiving on port: {} and replying with ACK on port: {}".format(self.inbound_port, self.outbound_port))
        
        while True:
            
            # receive data
            data = self.simulator.get_from_socket()
             
            corrupt = True
            correctSeqNo = False
            
            # check sequence number
            if (rcvSeqNo == expectedSeqNo)
                correctSeqNo = True
            else
                correctSeqNo = False

            # rcvChecksum is checksum received in packet
            # computedChecksum is checksum computed from packet
            if (rcvChecksum == computedChecksum)
                corrupt = False
            else
                corrupt = True             

            # check checksum
            if (correctSeqNo && !corrupt)
                # extract and deliver data
                # send ACK for seqNo
            else
                # send ACK for seqNo - 1

            
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
