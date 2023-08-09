import sys
import socket
import math
import random
import time
    
#default values for command line arguments
localIP     = "127.0.0.1"
bufferSize  = 2048
debug = False
RANDOM_DROP_PROB = 0.1
MAX_PACKETS = 10
localPort   = 20000
no_pkts_acked = 0

#actual command line parameters
n_args = len(sys.argv)
i = 1
while i<n_args:
    if(sys.argv[i]=="-d"):
       debug=True  
       i = i+1
    elif(sys.argv[i]=="-p"):
       localPort = int(sys.argv[i+1])
       i = i+2
    elif(sys.argv[i]=="-n"):
       MAX_PACKETS = int(sys.argv[i+1])
       i = i+2
    elif(sys.argv[i]=="-e"):
       RANDOM_DROP_PROB = float(sys.argv[i+1])
       i = i+2

# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
print("UDP server up and listening")

#next frame expected
NFE = 0
try:
  
  # Listen for incoming data packets
  bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
  message = bytesAddressPair[0].decode()
  
  if(message == "start_timer"):
       start_time = time.time()
  while True:
       bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
       message = bytesAddressPair[0].decode('unicode_escape')
       if(message == "bye"):
          break
       address = bytesAddressPair[1]
	    
       # to determine if packet is to be dropped, according to RANDOM_DROP_PROB
       inv_prob = 1/RANDOM_DROP_PROB
       inv_prob = math.floor(inv_prob)
       rand_num = random.randint(0,inv_prob-1)   #packet will be dropped if rand_num == 0
       
       ACK_pkt_temp = bytesAddressPair[0]
       ACK_num = ACK_pkt_temp[0]
       ACK_pkt = str(ACK_num)
       
       #calculate received time wrt start time
       curr_time = time.time()-start_time
       milliseconds = math.floor(curr_time*1000)
       microseconds = math.floor(curr_time*1000000-milliseconds*1000)
       
       if(rand_num%inv_prob != 0):     #packet not dropped
            if(int(ACK_num) == NFE):   #correct, inorder packet received
                if debug:
                   print("seq #",ACK_num," Time Received: ",milliseconds,":",microseconds," Packet Dropped: False")
                UDPServerSocket.sendto(ACK_pkt.encode(encoding="unicode_escape"), address)    #send ACK to sender
                NFE = (NFE+1) % 256
                no_pkts_acked += 1
            else:     #out-of-order packet dropped
                if debug:
                    print("seq #",ACK_num," Time Received: ",milliseconds,":",microseconds," Packet Dropped: True (out of order)")
       else:          #packet has been dropped
            if debug:
                print("seq #",ACK_num," Time Received: ",milliseconds,":",microseconds," Packet Dropped: True")
except KeyboardInterrupt:
	UDPServerSocket.close()
finally:
        UDPServerSocket.close()



