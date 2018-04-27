# ece308-error-channel-simulation

TCP segment structure: 1024 bits

sequence number: 32 bits (bits 0-31)

ack number: 32 bits (bits 32-63)

header length: 3 bits (bits 64-66)

ACK: 1 bit (bit 67)

unused: 60 bits (bits 68-127)

receive window: 32 bits (bits 128 - 159)

internet checksum: 32 bits (bits 160-191)

data: 832 bits (bits 192-1023)

