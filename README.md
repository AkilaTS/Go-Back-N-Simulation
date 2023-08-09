This is an implementation of the Go-back-N reliable transmission protocol. It also measures the round-trip delays. 

There are two separate programs running on two different hosts - a sender program that generates and transmits packets and a receiver that accepts the packets,
and transmits the acknowledgments to the sender. The sender and receiver communicate through UDP sockets. The receiver is implemented as a UDP server and the sender is implemented as a UDP client.

Command Line Options: 
The command line options provided to the sender are:
• -d – Turn ON Debug Mode (OFF if -d flag not present)
• -s string – Receiver Name or IP address.
• -p integer – Receiver’s Port Number
• -l integer – PACKET LENGTH, in bytes
• -r integer – PACKET GEN RATE, in packets per second
• -n integer – MAX PACKETS
• -w integer – WINDOW SIZE
• -f integer – MAX BUFFER SIZE

The command line options provided to the receiver are:
• -d – Turn ON Debug Mode (OFF if -d flag not present)
• -p integer – Receiver’s Port Number
• -n integer – MAX PACKETS
• -e float – Packet Error Rate (RANDOM DROP PROB)

Example command to run the sender process:
   python3 SenderGBN.py -s server_IP -p 20000 -l 128 -r 10 -n 100 -w 3 -b 10
   
Example command to run the receiver:
   python3 ReceiverGBN.py -p 12345 -n 400 -e 0.00001
   
In Debug mode, the receiver process prints the time at which each data packet is received. Packets are dropped with a random probability of RANDOM_PROB, specified by the command line parameter -e. Out of order packets are discarded. 

In Debug mode, the sender process prints the time at which the packet was generated, RTT for that packet and the total no of times the packet was transmitted until its ACK was received.

The sender and receiver outputs for several test runs have been recorded in the sender_script and receiver_script files respectively.
