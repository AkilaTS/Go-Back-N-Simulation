This is an implementation of the Go-back-N reliable transmission protocol. It also measures the round-trip delays. 

There are two separate programs running on two different hosts - a sender program that generates and transmits packets and a receiver that accepts the packets,
and transmits the acknowledgments to the sender. The sender and receiver communicate through UDP sockets. The receiver is implemented as a UDP server and the sender is implemented as a UDP client.

To run the receiver:
   python3 ReceiverGBN.py -p 12345 -n 400 -e 0.00001

To run the sender process:
   python3 SenderGBN.py -s server_IP -p 20000 -l 128 -r 10 -n 100 -w 3 -b 10
   
In Debug mode, the receiver process prints the time at which each data packet is received. Packets are dropped with a random probability of RANDOM_PROB, specified by the command line parameter -e. Out of order packets are discarded. 

In Debug mode, the sender process prints the time at which the packet was generated, RTT for that packet and the total no of times the packet was transmitted until its ACK was received.

The sender and receiver outputs for several test runs have been recorded in the sender_script and receiver_script files respectively.
