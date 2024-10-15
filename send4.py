import sys
import random
import time
import threading
from scapy.all import Ether, IP, UDP, Raw, sendp
from p4utils.utils.helper import load_topo
import multiprocessing
import controller

topo = load_topo('topology.json')


if len(sys.argv) > 1:
    duration = int(sys.argv[1])
else:
    duration = 10

target_bandwidth = 50*10**6
packet_size = 1470
packet_size_bits = packet_size * 8
#packet_interval = packet_size_bits / target_bandwidth
packet_interval  = 0.01
deadline_value= 5
deadline_value2= 7
deadline_value3= 9
deadline_value4= 10
deadline_value5= 12
deadline_value6= 15
deadline_value7= 18
deadline_value8= 20
weight = 1
weight2 = 2
weight3 = 3
weight4 = 4
weight5 = 5
weight6 = 6
weight7 = 7
weight8 = 8
flow_id = 0
flow_id2 = 1
flow_id3= 2
flow_id4 = 3
flow_id5 = 5
flow_id6 = 6
flow_id7 = 7
flow_id8 = 8
def send_udp_packet(src_ip, dst_ip, src_port, dst_port, deadline,weight,flow_id,iface):
    payload = deadline.to_bytes(8, byteorder='big') + weight.to_bytes(4, byteorder='big')+  flow_id.to_bytes(4, byteorder='big')

    udp_pkt = (Ether() /
               IP(src=src_ip, dst=dst_ip) /
               UDP(sport=src_port, dport=dst_port) /
               Raw(load=payload))
    print(f"Sending packet: {udp_pkt.summary()} on interface: {iface}")
    sendp(udp_pkt, iface=iface, verbose=False)

def send_packets(src_host, dst_host, iface, duration, packet_interval, deadline_value,weight,flow_id):

    src_ip = topo.get_host_ip(src_host)
    dst_ip = topo.get_host_ip(dst_host)

    src_port = random.randint(1025, 65000)
    dst_port = random.randint(1025, 65000)

    print(f"Source IP: {src_ip}, Destination IP: {dst_ip}, Interface: {iface}")
    print(f"Source Port: {src_port}, Destination Port: {dst_port}")

    total_packets = int(duration / packet_interval)

    for _ in range(total_packets):

        send_udp_packet(src_ip, dst_ip, src_port, dst_port, deadline_value, weight,flow_id, iface)
        time.sleep(packet_interval)


thread3 = threading.Thread(target=send_packets, args=('h5', 'h3', 's1-eth4', duration, packet_interval, deadline_value3,weight3,flow_id))
#thread5 = threading.Thread(target=send_packets, args=('h7', 'h3', 's1-eth4', duration, packet_interval, deadline_value5,weight5,flow_id))
#thread6 = threading.Thread(target=send_packets, args=('h8', 'h3', 's1-eth4', duration, packet_interval, deadline_value6,weight6,flow_id))
#thread7 = threading.Thread(target=send_packets, args=('h9', 'h3', 's1-eth4', duration, packet_interval, deadline_value6,weight6,flow_id))



thread3.start()

#thread5.start()
#thread6.start()
#thread7.start()


thread3.join()

#thread5.join()
#thread7.join()


#with open("stop_signal.txt", "w") as f:
#    f.write("Stop")
time.sleep(0.1)
