import sys
import os
import socket
import multiprocessing
from multiprocessing import Process, Manager
import time
import math

#default parameters
MAX_SEQ_NUM = 256  #8 bits used in sequence field
recv_IP = "127.0.0.1"
recv_port = 20000
PACKET_LENGTH = 5
PACKET_GEN_RATE = 20
MAX_PACKETS = 10
WINDOW_SIZE = 10
MAX_BUFFER_SIZE = 5

# Create a UDP socket at client side
UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)

#generates packets and stores them in the sender buffer(if space is available)
def worker_main(sbuf, gen_times):
    num_pkts = 0
    next_pkt = 0
    while(num_pkts<MAX_PACKETS):
        if(len(sbuf)<MAX_BUFFER_SIZE):
            sbuf.append(str(next_pkt))
            gen_times.append(time.time())
            next_pkt = ((next_pkt) + 1 ) % 256
            num_pkts = num_pkts + 1
        time.sleep(1/PACKET_GEN_RATE)

#receives the ACKs from the receiver
def receive_ACKS(sender_window, ACK_buffer):
   no_pkts_transmitted = 0     
   while((no_pkts_transmitted < MAX_PACKETS)):
            #Wait on recvfrom()
            msgFromServer = UDPClientSocket.recvfrom(bufferSize)
            ACK_pkt = msgFromServer[0].decode('unicode_escape')
            if(int(ACK_pkt)<sender_window[0]):
               continue
            #on receiving an ACK
            ACK_buffer.append(ACK_pkt)
            no_pkts_transmitted += 1
            
#actual command line parameters
n_args = len(sys.argv)
debug = False
i = 1
while i<n_args:
    if(sys.argv[i]=="-d"):
       debug=True 
       i = i+1
    elif(sys.argv[i]=="-s"):
       recv_IP = sys.argv[i+1]
       i = i+2
    elif(sys.argv[i]=="-p"):
       recv_port = int(sys.argv[i+1])
       i = i+2
    elif(sys.argv[i]=="-l"):
       PACKET_LENGTH = int(sys.argv[i+1])
       i = i+2
    elif(sys.argv[i]=="-r"):
       PACKET_GEN_RATE = int(sys.argv[i+1])
       i = i+2
    elif(sys.argv[i]=="-n"):
       MAX_PACKETS = int(sys.argv[i+1])
       i = i+2
    elif(sys.argv[i]=="-w"):
       WINDOW_SIZE = int(sys.argv[i+1])
       i = i+2
    elif(sys.argv[i]=="-b"):    #the parameter -b stands for MAX_BUFFER_SIZE
       MAX_BUFFER_SIZE = int(sys.argv[i+1])
       i = i+2

serverAddressPort   = (recv_IP, recv_port)
bufferSize          = 2048

#shared data structures
sender_buffer = Manager().list()
ACK_buffer = Manager().list()
pkt_times = Manager().list()
gen_times = Manager().list()
sender_window = Manager().list()
for l in range(WINDOW_SIZE):
   sender_window.append(l)
no_of_retrans = []
for k3 in range(WINDOW_SIZE):
   no_of_retrans.append(0)
   pkt_times.append(0.0)

#processes to generate packets and receive ACKs respectively
p = Process(target=worker_main, args=(sender_buffer,gen_times)) 
p.start()
p2 = Process(target=receive_ACKS, args=(sender_window,ACK_buffer)) 
p2.start()

#data packets has sequence number followed by dummy bytes (PACKET_LENGTH bytes in all)
packet = ""
for k4 in range(PACKET_LENGTH-1):
   packet = packet+"0"
packet = packet.encode(encoding="unicode_escape")

#to track statistics
Max_Trans_Reached = False
no_pkts_trans = 0
avg_RTT = 1
curr_timeout = 0.1  #100 ms for first 10 packets, latter set to 2*avg_RTT ms
total_trans = 0
total_RTT = 0.0
try:
    #start_time wrt to which other timestamps are calculated
    start_time = time.time()
    temp_str = "start_timer"
    bytesToSend = temp_str.encode()
    UDPClientSocket.sendto(bytesToSend, serverAddressPort) 
       
    while((no_pkts_trans < MAX_PACKETS) and (not Max_Trans_Reached)):
        #transmit WS no of packets
        i1 = 0
        
        while(i1<len(sender_buffer) and i1<WINDOW_SIZE):
            item = sender_buffer[i1]
            curr_pkt_num = int(item)
            curr_pkt_num_byte = curr_pkt_num.to_bytes(1,byteorder="little")
            curr_pkt = curr_pkt_num_byte + packet
            bytesToSend = curr_pkt
            
            #restart timer for this packet
            pkt_times[i1]=time.time()
            no_of_retrans[i1] = no_of_retrans[i1] + 1  #another retransmission attempt for this packet
            if(no_of_retrans[i1]>6):
               Max_Trans_Reached = True   #sender has to terminate
               break
            UDPClientSocket.sendto(bytesToSend, serverAddressPort)      #send packet
            total_trans += 1     #one more packet transmitted
            i1 += 1
        
        if(Max_Trans_Reached):
            break  #terminate sender
            
        if(len(pkt_times)<=0):
            continue
        while(time.time()<pkt_times[0]+curr_timeout):
            if(len(ACK_buffer)<=0):
               continue
            ACK_pkt = ACK_buffer[0]
            ACK_buffer.pop(0)
            curr_time = pkt_times[0]-start_time
            pkt_gen_time = gen_times[0] - start_time
            milliseconds = math.floor(pkt_gen_time*1000)
            microseconds = math.floor(pkt_gen_time*1000000-milliseconds*1000)
            curr_RTT = time.time() - pkt_times[0]
            #expected ACK has been received
            if debug:
                print("seq #",ACK_pkt," Time Generated: ",milliseconds,":",microseconds," RTT: ",curr_RTT*1000," ms"," Number of Attempts: ",no_of_retrans[0])
                
            #update avg_RTT and timeout
            avg_RTT = avg_RTT*no_pkts_trans + curr_RTT
            no_pkts_trans += 1     
            avg_RTT = avg_RTT/no_pkts_trans 
            if(no_pkts_trans>10):
                curr_timeout = 2*avg_RTT
            start_of_window = int(sender_window[0])
            acked_index = int(ACK_pkt)
            no_acked = (acked_index-start_of_window+1)%WINDOW_SIZE
            
            #remove ACKed packets from sender buffer and slide the sender window
            for l1 in range(no_acked):
              if(len(sender_buffer)>0):
                 sender_buffer.pop(0)
                 pkt_times.pop(0)
                 no_of_retrans.pop(0)
                 gen_times.pop(0)
            for l1 in range(no_acked):
               sender_window.pop(0)
            
            while(len(sender_window)<WINDOW_SIZE):
               curr_last = sender_window[-1]
               to_add = (curr_last+1) % MAX_SEQ_NUM
               sender_window.append(to_add) 
               no_of_retrans.append(0)
               pkt_times.append(0.0)
      
            if(len(pkt_times)<=0):
               break   
    
    if(no_pkts_trans != 0):
       retrans_ratio = total_trans/no_pkts_trans
    else:
       retrans_ratio = 0
    
    #display statistics
    print("\nPACKET_GEN_RATE: ",PACKET_GEN_RATE," packets per s")
    print("PACKET_LENGTH: ",PACKET_LENGTH," bytes")
    print("Retransmisson Ratio: ",retrans_ratio)
    print("Average RTT for all acknowledged packets: ",avg_RTT*1000," ms")   
except KeyboardInterrupt:
	UDPClientSocket.close()
finally:
    p.terminate()
    p2.terminate()
    term_msg = "bye"
    UDPClientSocket.sendto(term_msg.encode(encoding="unicode_escape"), serverAddressPort)
    UDPClientSocket.close()
