# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 15:41:38 2018

@author: brettstephen
"""
import channelsimulator

def checksum(packet): # computes in int, returns binary
        p_list = list(packet) # list of data as 8-bit integers
        w_list = [] # list of 16-bit integer words
        for i in range(0,len(p_list)-1):
            if i%2 == 0:
                h1 = int("{:08b}".format(p_list[i]) + "{:08b}".format(p_list[i+1]),2)
                w_list.append(h1)
        MOD = 1 << 16
        check = 0
        for w in w_list: # summation
            check += w
            if check > MOD:
                check = (check+1) % MOD # overflow wrap-around
        cs = "{:016b}".format(~check & 0xffff)
        check_sum = [int(cs[0:8],2), int(cs[8:16],2)]
        return check_sum
    
class Segment(object):
    HEAD_LEN = [int('01000000',2), 0] # 4 32-bit words, with unused space
    
    def _init_(self): # still have not included src/dest port #s
        self.seq_num = [0,0,0,0] # 32-bit 0
        self.ack_num = [0,0,0,0] # 32-bit 0
        self.checks = [0,0]
    
    def make_pkt(self,seqn,ackn,rcv_win,data_bytes):
        """
        Get data from socket
        :return: bit string of header data
        """
        
        sq = "{:032b}".format(seqn)
        ac = "{:032b}".format(ackn)
        rw = "{:016b}".format(rcv_win)
        self.seq_num = [int(sq[0:8],2), int(sq[8:16],2), int(sq[16:24],2), int(sq[24:32],2)]
        self.ack_num = [int(ac[0:8],2), int(ac[8:16],2), int(ac[16:24],2), int(ac[24:32],2)]
        rcv_w = [int(rw[0:8],2), int(rw[8:16],2)]
        header = self.seq_num + self.ack_num + self.HEAD_LEN + rcv_w + [0,0] + [0,0]
        packet = bytearray(header) + data_bytes
        header[12:14] = checksum(packet)
        packet = bytearray(header) + data_bytes
        return packet
    
if __name__ == "__main__":
    # test out BogoSender
    seg = Segment()
    h = channelsimulator.random_bytes(190)
    p = seg.make_pkt(10000,1000,500,h)
    print checksum(p)
    