# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 15:41:38 2018

@author: brettstephen
"""
import channelsimulator

class Segment(object):
    
    def _init_(self): # still have not included src/dest port #s
        self.seq_num = [0,0,0,0] # 32-bit 0
        self.ack_num = [0,0,0,0] # 32-bit 0
        self.head_len = [int(01000000), 0] # 4 32-bit words, with unused space
        self.rcv_win = [0,0]
        self.checks = [0,0]
        
    def checksum(packet): # computes in int, returns binary
        p_list = list(packet) # list of data as 8-bit integers
        w_list = [] # list of 16-bit integer words
        for n in p_list:
            if n%2 == 0:
                h1 = int("{:08b}".format(p_list[n]) + "{:08b}".format(p_list[n+1]),2)
                w_list.append(h1)
        MOD = 1 << 16
        check = 0
        for w in w_list: # summation
            check += w
            if check > MOD:
                check = (check+1) % MOD # overflow wrap-around
        cs = "{:016b}".format(~check)
        check_sum = [str(int(cs,2))[0:8], str(int(cs,2))[8:15]]
        
        return ~check
    
    def make_pkt(self,seqn,ackn,data_bytes):
        """
        Get data from socket
        :return: bit string of header data
        """
        
        self.seq_num = [seqn]
        self.ack_num = [ackn]
        header = self.seq_num + self.ack_num + self.head_len + self.rcv_win + self.checks
        packet = bytearray(header).append(data_bytes)
        self.checksum = Segment.checksum(packet)
        header[10] = self.checks
        packet = bytearray(header).append(data_bytes)
        return packet
    
if __name__ == "__main__":
    # test out BogoSender
    seg = Segment()
    h = channelsimulator.random_bytes(512)